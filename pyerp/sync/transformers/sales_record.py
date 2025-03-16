"""Transformer for sales records from legacy ERP system."""

import re
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional

from django.utils.text import slugify
from pyerp.utils.logging import get_logger

from .base import BaseTransformer


logger = get_logger(__name__)


class SalesRecordTransformer(BaseTransformer):
    """Transforms sales record data from legacy ERP to Django model format."""

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a sales record from legacy format to Django model format.
        
        Args:
            data: Raw data from the legacy system
            
        Returns:
            Transformed data ready for loading into Django models
        """
        try:
            # Basic validation
            if not data:
                logger.warning("Empty data received for transformation")
                return {}
                
            if 'AbsNr' not in data:
                logger.warning("Missing AbsNr in sales record data")
                return {}
                
            # Transform the record
            transformed = {
                'legacy_id': data.get('AbsNr'),
                'record_number': str(data.get('PapierNr', '')),
                'record_date': self._parse_legacy_date(data.get('Datum')),
                'record_type': self._map_record_type(data.get('Papierart')),
                'customer_id': data.get('KundenNr'),  # Will be resolved to actual customer by loader
                'status': self._map_status(data),
                
                # Financial fields
                'subtotal': self._to_decimal(data.get('Netto', 0)),
                'tax_amount': self._to_decimal(data.get('MWST_EUR', 0)),
                'shipping_cost': self._to_decimal(data.get('Frachtkosten', 0)),
                'handling_fee': self._to_decimal(data.get('Bearbeitungskos', 0)),
                'discount_amount': self._calculate_discount(data),
                'total_amount': self._to_decimal(data.get('Endbetrag', 0)),
                
                # Payment information
                'payment_terms': self._extract_payment_terms(data),
                'payment_method': self._extract_payment_method(data),
                'payment_status': data.get('bezahlt', False),
                'payment_date': self._parse_legacy_date(data.get('ZahlungsDat')),
                'due_date': self._calculate_due_date(data),
                
                # Currency information
                'currency': self._map_currency(data.get('Währung')),
                'exchange_rate': self._get_exchange_rate(data.get('Währung')),
                
                # Address information
                'shipping_address': self._extract_shipping_address(data),
                'billing_address': self._extract_billing_address(data),
                
                # Tax information
                'tax_type': data.get('MWSt_Art', ''),
                'tax_rate': self._extract_tax_rate(data),
                
                # Additional information
                'notes': data.get('Text', ''),
                'internal_notes': '',
                
                # Source information
                'source_system': 'LEGACY',
            }
            
            return transformed
            
        except Exception as e:
            logger.error(f"Error transforming sales record {data.get('AbsNr')}: {str(e)}")
            raise
            
    def transform_line_items(self, data: List[Dict[str, Any]], parent_id: int) -> List[Dict[str, Any]]:
        """
        Transform sales record line items from legacy format to Django model format.
        
        Args:
            data: List of raw line item data from the legacy system
            parent_id: ID of the parent sales record in the Django system
            
        Returns:
            List of transformed line items ready for loading
        """
        transformed_items = []
        
        for item in data:
            try:
                if not item or 'AbsNr' not in item or 'PosNr' not in item:
                    continue
                    
                transformed_item = {
                    'legacy_id': f"{item.get('AbsNr')}_{item.get('PosNr')}",
                    'sales_record_id': parent_id,
                    'position': item.get('PosNr'),
                    'product_code': item.get('ArtNr', ''),
                    'description': item.get('Bezeichnung', ''),
                    'quantity': self._to_decimal(item.get('Menge', 0)),
                    'unit_price': self._to_decimal(item.get('Preis', 0)),
                    'discount_percentage': self._to_decimal(item.get('Rabatt', 0)),
                    'tax_rate': self._extract_line_item_tax_rate(item),
                    'tax_amount': self._calculate_line_item_tax(item),
                    'line_subtotal': self._calculate_line_subtotal(item),
                    'line_total': self._to_decimal(item.get('Pos_Betrag', 0)),
                    'item_type': self._map_item_type(item.get('Art')),
                    'notes': '',
                    'fulfillment_status': self._map_fulfillment_status(item),
                    'fulfilled_quantity': self._to_decimal(item.get('Pick_Menge', 0)),
                }
                
                transformed_items.append(transformed_item)
                
            except Exception as e:
                logger.error(f"Error transforming line item {item.get('AbsNr')}_{item.get('PosNr')}: {str(e)}")
                continue
                
        return transformed_items
    
    def _parse_legacy_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse legacy date format (D!M!Y) to ISO format."""
        if not date_str or date_str == '0!0!0':
            return None
            
        try:
            day, month, year = date_str.split('!')
            # Handle 2-digit years
            if len(year) == 2:
                year = '19' + year if int(year) > 50 else '20' + year
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except Exception:
            logger.warning(f"Could not parse legacy date: {date_str}")
            return None
    
    def _map_record_type(self, type_code: Optional[str]) -> str:
        """Map legacy record type codes to new system values."""
        type_mapping = {
            'R': 'INVOICE',
            'A': 'PROPOSAL',
            'L': 'DELIVERY_NOTE',
            'G': 'CREDIT_NOTE',
            'B': 'ORDER_CONFIRMATION',
        }
        return type_mapping.get(type_code, 'INVOICE')
    
    def _map_status(self, data: Dict[str, Any]) -> str:
        """Determine the status based on legacy data."""
        if data.get('bezahlt'):
            return 'PAID'
        
        # Check if overdue
        due_date = self._calculate_due_date(data)
        if due_date and due_date < datetime.now().strftime('%Y-%m-%d'):
            return 'OVERDUE'
            
        return 'PENDING'
    
    def _to_decimal(self, value) -> Decimal:
        """Convert value to Decimal, handling various input types."""
        if value is None:
            return Decimal('0')
        try:
            return Decimal(str(value))
        except:
            return Decimal('0')
    
    def _calculate_discount(self, data: Dict[str, Any]) -> Decimal:
        """Calculate discount amount from percentage if available."""
        rabatt = self._to_decimal(data.get('Rabatt', 0))
        netto = self._to_decimal(data.get('Netto', 0))
        
        if rabatt > 0:
            return (rabatt * netto) / Decimal('100')
        return Decimal('0')
    
    def _extract_payment_terms(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract payment terms information for lookup or creation."""
        return {
            'days_due': int(data.get('NettoTage', 30)),
            'discount_days': int(data.get('SkontoTage', 0)),
            'discount_percent': self._to_decimal(data.get('Skonto_G', 0)),
        }
    
    def _extract_payment_method(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract payment method information for lookup or creation."""
        return {
            'name': data.get('Zahlungsart_A', 'Invoice'),
            'code': slugify(data.get('Zahlungsart_A', 'invoice')),
        }
    
    def _calculate_due_date(self, data: Dict[str, Any]) -> Optional[str]:
        """Calculate due date based on invoice date and payment terms."""
        invoice_date = self._parse_legacy_date(data.get('Datum'))
        if not invoice_date:
            return None
            
        try:
            date_obj = datetime.strptime(invoice_date, '%Y-%m-%d')
            days_due = int(data.get('NettoTage', 30))
            due_date = date_obj.replace(day=date_obj.day + days_due)
            return due_date.strftime('%Y-%m-%d')
        except Exception:
            logger.warning(f"Could not calculate due date for record {data.get('AbsNr')}")
            return None
    
    def _map_currency(self, currency_code: Optional[str]) -> str:
        """Map legacy currency codes to ISO codes."""
        currency_mapping = {
            'DM': 'EUR',  # Deutsche Mark to Euro
            'EUR': 'EUR',
            'USD': 'USD',
            'GBP': 'GBP',
        }
        return currency_mapping.get(currency_code, 'EUR')
    
    def _get_exchange_rate(self, currency_code: Optional[str]) -> Decimal:
        """Get exchange rate for currency conversion if needed."""
        if currency_code == 'DM':
            return Decimal('1.95583')  # Fixed DM to EUR conversion rate
        return Decimal('1.0')
    
    def _extract_shipping_address(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize shipping address."""
        address_str = data.get('Lief_Adr', '')
        return self._parse_address(address_str)
    
    def _extract_billing_address(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize billing address."""
        address_str = data.get('Rech_Adr', '')
        return self._parse_address(address_str)
    
    def _parse_address(self, address_str: str) -> Dict[str, Any]:
        """Parse address string into structured format."""
        if not address_str:
            return {}
            
        # Split address by line breaks
        parts = address_str.split('\\r')
        
        # Basic parsing - this would need to be enhanced based on actual data format
        result = {
            'raw': address_str,
            'name': parts[0] if len(parts) > 0 else '',
            'street': parts[1] if len(parts) > 1 else '',
            'city': '',
            'postal_code': '',
            'country': 'DE',  # Default to Germany
        }
        
        # Try to extract postal code and city from the third line
        if len(parts) > 2:
            city_line = parts[2]
            postal_match = re.search(r'(\d{5})\s+(.*)', city_line)
            if postal_match:
                result['postal_code'] = postal_match.group(1)
                result['city'] = postal_match.group(2)
            else:
                result['city'] = city_line
        
        return result
    
    def _extract_tax_rate(self, data: Dict[str, Any]) -> Decimal:
        """Extract tax rate from data or use default."""
        # This would need to be adjusted based on actual data
        tax_type = data.get('MWSt_Art', '')
        if tax_type == 'JA':
            return Decimal('19.0')  # Standard German VAT rate
        elif tax_type == 'incl.':
            return Decimal('19.0')  # Included VAT
        return Decimal('0.0')
    
    def _extract_line_item_tax_rate(self, item: Dict[str, Any]) -> Decimal:
        """Extract tax rate for line item."""
        # This would need to be adjusted based on actual data
        return Decimal('19.0')  # Default to standard German VAT
    
    def _calculate_line_item_tax(self, item: Dict[str, Any]) -> Decimal:
        """Calculate tax amount for line item."""
        subtotal = self._calculate_line_subtotal(item)
        tax_rate = self._extract_line_item_tax_rate(item)
        return (subtotal * tax_rate) / Decimal('100')
    
    def _calculate_line_subtotal(self, item: Dict[str, Any]) -> Decimal:
        """Calculate subtotal for line item (before tax)."""
        quantity = self._to_decimal(item.get('Menge', 0))
        price = self._to_decimal(item.get('Preis', 0))
        discount = self._to_decimal(item.get('Rabatt', 0))
        
        subtotal = quantity * price
        if discount > 0:
            subtotal = subtotal * (1 - (discount / Decimal('100')))
        
        return subtotal
    
    def _map_item_type(self, type_code: Optional[str]) -> str:
        """Map legacy item type codes to new system values."""
        type_mapping = {
            'L': 'PRODUCT',
            'S': 'SERVICE',
            'T': 'TEXT',
            'D': 'DISCOUNT',
        }
        return type_mapping.get(type_code, 'PRODUCT')
    
    def _map_fulfillment_status(self, item: Dict[str, Any]) -> str:
        """Determine fulfillment status based on legacy data."""
        if item.get('Picking_ok', False):
            return 'FULFILLED'
            
        pick_menge = self._to_decimal(item.get('Pick_Menge', 0))
        menge = self._to_decimal(item.get('Menge', 0))
        
        if pick_menge > 0 and pick_menge < menge:
            return 'PARTIAL'
        elif pick_menge >= menge:
            return 'FULFILLED'
            
        return 'PENDING' 
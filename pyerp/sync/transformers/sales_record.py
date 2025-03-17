"""Transformer for sales records from legacy ERP system."""

import re
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional

from django.utils.text import slugify
from pyerp.utils.logging import get_logger, log_data_sync_event

from .base import BaseTransformer


logger = get_logger(__name__)


class SalesRecordTransformer(BaseTransformer):
    """Transforms sales record data from legacy ERP to Django model format."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the transformer with configuration.
        
        Args:
            config: Dictionary containing transformer configuration
        """
        super().__init__(config)

    def transform(self, data: Any) -> Dict[str, Any]:
        """
        Transform data from legacy format to Django model format.
        
        Args:
            data: Raw data from the legacy system (single record or list)
            
        Returns:
            Transformed data ready for loading into Django models
        """
        # Handle string inputs
        if isinstance(data, str):
            logger.warning(f"Received string data instead of dictionary: {data[:100]}...")
            return {}
            
        # Handle dictionary inputs
        if isinstance(data, dict):
            return self._transform_single_record(data)
            
        # Handle any other unexpected input
        logger.warning(f"Received unexpected data type: {type(data)}")
        return {}
            
    def _transform_single_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single sales record from legacy format to Django model format.
        
        Args:
            data: Raw data for a single record from the legacy system
            
        Returns:
            Transformed data ready for loading into Django models
        """
        try:
            # Basic validation
            if not data:
                logger.warning("Empty data received for transformation")
                log_data_sync_event(
                    source="legacy_erp",
                    destination="pyerp",
                    record_count=0,
                    status="transform_error",
                    details={
                        "error": "Empty data received",
                        "entity_type": "sales_record"
                    }
                )
                return {}
                
            if 'AbsNr' not in data:
                logger.warning("Missing AbsNr in sales record data")
                log_data_sync_event(
                    source="legacy_erp",
                    destination="pyerp",
                    record_count=0,
                    status="transform_error",
                    details={
                        "error": "Missing AbsNr in data",
                        "entity_type": "sales_record",
                        "data_keys": list(data.keys())
                    }
                )
                return {}
                
            # Get or create customer
            customer = self._get_or_create_customer(data)
            if not customer:
                logger.warning(f"Could not find or create customer for record {data.get('AbsNr')}")
                log_data_sync_event(
                    source="legacy_erp",
                    destination="pyerp",
                    record_count=0,
                    status="transform_error",
                    details={
                        "error": "Customer lookup failed",
                        "entity_type": "sales_record",
                        "record_id": data.get('AbsNr'),
                        "customer_id": data.get('KundenNr')
                    }
                )
                return {}
            
            # Get or create payment terms
            payment_terms = self._extract_payment_terms(data)
            if not payment_terms:
                logger.warning(f"Could not create payment terms for record {data.get('AbsNr')}")
                return {}
            
            # Get or create payment method
            payment_method = self._extract_payment_method(data)
            if not payment_method:
                logger.warning(f"Could not create payment method for record {data.get('AbsNr')}")
                return {}
            
            # Get or create shipping method
            shipping_method = self._extract_shipping_method(data)
            if not shipping_method:
                logger.warning(f"Could not create shipping method for record {data.get('AbsNr')}")
                return {}
            
            # Get or create shipping address
            shipping_address = self._extract_shipping_address(data)
            if not shipping_address:
                logger.warning(f"Could not create shipping address for record {data.get('AbsNr')}")
                # Continue without shipping address since it's now optional
            
            # Get or create billing address
            billing_address = self._extract_billing_address(data)
            if not billing_address:
                logger.warning(f"Could not create billing address for record {data.get('AbsNr')}")
                # Continue without billing address since it's now optional
            
            # Parse dates
            record_date = self._parse_legacy_date(data.get('Datum'))
            if not record_date:
                logger.warning(f"Could not parse record date for record {data.get('AbsNr')}")
                return {}
            
            # Calculate due date
            due_date = self._calculate_due_date(data)
            if not due_date:
                # Use record date + 30 days as fallback
                try:
                    from datetime import datetime, timedelta
                    date_obj = datetime.strptime(record_date, '%Y-%m-%d')
                    due_date = (date_obj + timedelta(days=30)).strftime('%Y-%m-%d')
                except Exception:
                    logger.warning(f"Could not calculate due date for record {data.get('AbsNr')}")
                    return {}
            
            # Transform the record
            transformed = {
                'legacy_id': data.get('AbsNr'),
                'record_number': str(data.get('PapierNr', '')),
                'record_date': record_date,
                'record_type': self._map_record_type(data.get('Papierart')),
                'customer': customer,
                'status': self._map_status(data),
                
                # Financial fields
                'subtotal': self._to_decimal(data.get('Netto', 0)),
                'tax_amount': self._to_decimal(data.get('MWST_EUR', 0)),
                'shipping_cost': self._to_decimal(data.get('Frachtkosten', 0)),
                'handling_fee': self._to_decimal(data.get('Bearbeitungskos', 0)),
                'discount_amount': self._calculate_discount(data),
                'total_amount': self._to_decimal(data.get('Endbetrag', 0)),
                
                # Payment information
                'payment_terms': payment_terms,
                'payment_method': payment_method,
                'payment_status': self._map_payment_status(data.get('bezahlt', False)),
                'payment_date': self._parse_legacy_date(data.get('ZahlungsDat')),
                'due_date': due_date,
                
                # Currency information
                'currency': self._map_currency(data.get('Währung')),
                'exchange_rate': self._get_exchange_rate(data.get('Währung')),
                
                # Shipping information
                'shipping_method': shipping_method,
                'shipping_address': shipping_address,
                'billing_address': billing_address,
                
                # Tax information
                'tax_type': data.get('MWSt_Art', ''),
                'tax_rate': self._extract_tax_rate(data),
                
                # Additional information
                'notes': data.get('Text', ''),
                'internal_notes': '',
                
                # Source information
                'source_system': 'LEGACY',
            }
            
            logger.debug(f"Transformed record {data.get('AbsNr')}: {transformed}")
            
            # Log successful transformation
            log_data_sync_event(
                source="legacy_erp",
                destination="pyerp",
                record_count=1,
                status="transformed",
                details={
                    "entity_type": "sales_record",
                    "record_id": data.get('AbsNr'),
                    "record_type": transformed.get('record_type')
                }
            )
            
            return transformed
            
        except Exception as e:
            logger.error(f"Error transforming sales record {data.get('AbsNr', 'unknown')}: {str(e)}")
            logger.exception("Transformation error details:")
            
            # Log transformation error
            log_data_sync_event(
                source="legacy_erp",
                destination="pyerp",
                record_count=0,
                status="transform_exception",
                details={
                    "entity_type": "sales_record",
                    "record_id": data.get('AbsNr', 'unknown'),
                    "error": str(e)
                }
            )
            
            return {}
            
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
        
        if not data:
            logger.warning(f"No line items found for parent_id {parent_id}")
            log_data_sync_event(
                source="legacy_erp",
                destination="pyerp",
                record_count=0,
                status="transform_warning",
                details={
                    "entity_type": "sales_record_item",
                    "parent_id": parent_id,
                    "warning": "No line items found"
                }
            )
            return []
            
        # Verify parent record exists
        from pyerp.business_modules.sales.models import SalesRecord
        try:
            parent_record = SalesRecord.objects.get(id=parent_id)
            logger.info(f"Found parent record with ID {parent_id} (legacy_id: {parent_record.legacy_id})")
        except SalesRecord.DoesNotExist:
            logger.error(f"Parent sales record with ID {parent_id} not found")
            log_data_sync_event(
                source="legacy_erp",
                destination="pyerp",
                record_count=0,
                status="transform_error",
                details={
                    "entity_type": "sales_record_item",
                    "parent_id": parent_id,
                    "error": "Parent record not found"
                }
            )
            return []
        
        # Handle case when data is a list of lists
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
            logger.info(f"Received a list of lists for line items, converting to list of dicts")
            # Convert list of lists to list of dicts
            new_data = []
            for item_list in data:
                if isinstance(item_list, dict):
                    new_data.append(item_list)
                else:
                    logger.warning(f"Unexpected data format for line item: {item_list}")
            data = new_data
        
        # Filter items to match parent record's legacy_id
        parent_legacy_id = parent_record.legacy_id
        filtered_data = []
        for item in data:
            if item.get('AbsNr') == parent_legacy_id:
                filtered_data.append(item)
            
        if not filtered_data:
            logger.warning(f"No matching line items found for parent legacy_id {parent_legacy_id}")
            return []
            
        logger.info(f"Processing {len(filtered_data)} line items for parent_id {parent_id} (legacy_id: {parent_legacy_id})")
        
        successful_items = 0
        failed_items = 0
        
        for item in filtered_data:
            try:
                if not item or 'AbsNr' not in item or 'PosNr' not in item:
                    logger.warning(f"Invalid line item data for parent_id {parent_id}: {item}")
                    failed_items += 1
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
                successful_items += 1
            except Exception as e:
                logger.error(f"Error transforming line item: {e}", exc_info=True)
                failed_items += 1
        
        logger.info(f"Transformed {successful_items} line items successfully, {failed_items} failed")
        
        if successful_items == 0:
            logger.warning(f"No line items were successfully transformed for parent_id {parent_id}")
            
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
    
    def _map_payment_status(self, paid: bool) -> str:
        """Map boolean payment status to string status."""
        return 'PAID' if paid else 'PENDING'
    
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
    
    def _extract_payment_terms(self, data: Dict[str, Any]) -> Optional[Any]:
        """Extract payment terms from data or create default."""
        try:
            from pyerp.business_modules.sales.models import PaymentTerms
            
            days_due = int(data.get('NettoTage', 30))
            discount_days = int(data.get('SkontoTage', 0))
            discount_percent = self._to_decimal(data.get('Skonto_G', 0))
            
            # Get or create payment terms
            payment_terms, created = PaymentTerms.objects.get_or_create(
                days_due=days_due,
                discount_days=discount_days,
                discount_percent=discount_percent,
                defaults={
                    'name': f"{discount_percent}% {discount_days} days, net {days_due}"
                }
            )
            
            return payment_terms
        except Exception as e:
            logger.error(f"Error extracting payment terms: {e}")
            return None
    
    def _extract_payment_method(self, data: Dict[str, Any]) -> Optional[Any]:
        """Extract payment method from data or create default."""
        try:
            from pyerp.business_modules.sales.models import PaymentMethod
            from django.utils.text import slugify
            
            name = data.get('Zahlungsart_A', 'Invoice')
            if not name:
                name = 'Invoice'
            
            code = slugify(name)
            
            # Get or create payment method
            payment_method, created = PaymentMethod.objects.get_or_create(
                name=name,
                defaults={
                    'code': code
                }
            )
            
            return payment_method
        except Exception as e:
            logger.error(f"Error extracting payment method: {e}")
            return None
    
    def _extract_shipping_method(self, data: Dict[str, Any]) -> Optional[Any]:
        """Extract shipping method from data or create default."""
        try:
            from pyerp.business_modules.sales.models import ShippingMethod
            from django.utils.text import slugify
            
            name = data.get('Versandart', 'Standard')
            if not name:
                name = 'Standard'
                
            code = slugify(name)
            
            # Get or create shipping method
            shipping_method, created = ShippingMethod.objects.get_or_create(
                name=name,
                defaults={
                    'code': code
                }
            )
            
            return shipping_method
        except Exception as e:
            logger.error(f"Error extracting shipping method: {e}")
            return None
    
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
    
    def _extract_shipping_address(self, data: Dict[str, Any]) -> Optional[Any]:
        """Extract shipping address from data or create default."""
        try:
            from pyerp.business_modules.sales.models import Address, Customer
            
            address_str = data.get('Lief_Adr', '')
            if not address_str:
                return None
            
            # Parse address
            parsed = self._parse_address(address_str)
            
            # Try to find customer
            customer_id = data.get('KundenNr')
            customer = None
            if customer_id:
                try:
                    customer = Customer.objects.get(legacy_id=customer_id)
                except Customer.DoesNotExist:
                    # Try to find by customer_number
                    try:
                        customer = Customer.objects.get(customer_number=str(customer_id))
                    except Customer.DoesNotExist:
                        logger.warning(f"Customer not found for shipping address, record {data.get('AbsNr')}")
                        return None
            
            if not customer:
                logger.warning(f"No customer found for shipping address, record {data.get('AbsNr')}")
                return None
            
            # Create a unique identifier for this address
            address_hash = hash(address_str)
            
            # Ensure we have required fields
            street = parsed.get('street', '')
            if not street and len(parsed.get('raw', '').split('\r')) > 1:
                street = parsed.get('raw', '').split('\r')[1]
            
            city = parsed.get('city', '')
            if not city and len(parsed.get('raw', '').split('\r')) > 2:
                city = parsed.get('raw', '').split('\r')[2]
            
            # Check if address already exists for this customer
            try:
                # First try to find by legacy_id
                existing_address = Address.objects.filter(
                    customer=customer,
                    legacy_id=f"shipping_{address_hash}"
                ).first()
                
                if existing_address:
                    logger.info(f"Found existing shipping address for customer {customer.id}")
                    return existing_address
                
                # Try to find by street and city
                existing_address = Address.objects.filter(
                    customer=customer,
                    street=street,
                    city=city
                ).first()
                
                if existing_address:
                    logger.info(f"Found existing shipping address by street/city for customer {customer.id}")
                    return existing_address
                
                # Get or create address with is_primary=False to avoid unique constraint violation
                address, created = Address.objects.get_or_create(
                    customer=customer,
                    legacy_id=f"shipping_{address_hash}",
                    defaults={
                        'street': street,
                        'city': city,
                        'postal_code': parsed.get('postal_code', ''),
                        'country': parsed.get('country', 'DE'),
                        'company_name': parsed.get('name', ''),
                        'is_primary': False
                    }
                )
                
                return address
            except Exception as e:
                logger.error(f"Error creating shipping address: {e}", exc_info=True)
                
                # Check if the error is due to unique constraint on is_primary
                if "unique_primary_address_per_customer" in str(e):
                    try:
                        # Try to create a non-primary address
                        address = Address.objects.create(
                            customer=customer,
                            legacy_id=f"shipping_{address_hash}_non_primary",
                            street=street or "Unknown",
                            city=city or "Unknown",
                            postal_code=parsed.get('postal_code', '00000'),
                            country='DE',
                            company_name=parsed.get('name', ''),
                            is_primary=False
                        )
                        logger.info(f"Created non-primary shipping address for customer {customer.id}")
                        return address
                    except Exception as e2:
                        logger.error(f"Failed to create non-primary shipping address: {e2}", exc_info=True)
                
                # Fallback: Create a minimal valid address with unique legacy_id
                try:
                    import uuid
                    unique_suffix = str(uuid.uuid4())[:8]
                    address = Address.objects.create(
                        customer=customer,
                        legacy_id=f"shipping_{address_hash}_{unique_suffix}",
                        street=street or "Unknown",
                        city=city or "Unknown",
                        postal_code=parsed.get('postal_code', '00000'),
                        country='DE',
                        company_name=parsed.get('name', ''),
                        is_primary=False
                    )
                    logger.info(f"Created fallback shipping address for customer {customer.id}")
                    return address
                except Exception as e2:
                    logger.error(f"Fallback address creation failed: {e2}", exc_info=True)
                    return None
        except Exception as e:
            logger.error(f"Error extracting shipping address: {e}", exc_info=True)
            return None
    
    def _extract_billing_address(self, data: Dict[str, Any]) -> Optional[Any]:
        """Extract billing address from data or create default."""
        try:
            from pyerp.business_modules.sales.models import Address, Customer
            
            address_str = data.get('Rech_Adr', '')
            if not address_str:
                # If no billing address, use shipping address
                if data.get('Lief_Adr'):
                    return self._extract_shipping_address(data)
                return None
            
            # Parse address
            parsed = self._parse_address(address_str)
            
            # Try to find customer
            customer_id = data.get('KundenNr')
            customer = None
            if customer_id:
                try:
                    customer = Customer.objects.get(legacy_id=customer_id)
                except Customer.DoesNotExist:
                    # Try to find by customer_number
                    try:
                        customer = Customer.objects.get(customer_number=str(customer_id))
                    except Customer.DoesNotExist:
                        logger.warning(f"Customer not found for billing address, record {data.get('AbsNr')}")
                        return None
            
            if not customer:
                logger.warning(f"No customer found for billing address, record {data.get('AbsNr')}")
                return None
            
            # Create a unique identifier for this address
            address_hash = hash(address_str)
            
            # Ensure we have required fields
            street = parsed.get('street', '')
            if not street and len(parsed.get('raw', '').split('\r')) > 1:
                street = parsed.get('raw', '').split('\r')[1]
            
            city = parsed.get('city', '')
            if not city and len(parsed.get('raw', '').split('\r')) > 2:
                city = parsed.get('raw', '').split('\r')[2]
            
            # Check if address already exists for this customer
            try:
                # First try to find by legacy_id
                existing_address = Address.objects.filter(
                    customer=customer,
                    legacy_id=f"billing_{address_hash}"
                ).first()
                
                if existing_address:
                    logger.info(f"Found existing billing address for customer {customer.id}")
                    return existing_address
                
                # Try to find by street and city
                existing_address = Address.objects.filter(
                    customer=customer,
                    street=street,
                    city=city
                ).first()
                
                if existing_address:
                    logger.info(f"Found existing billing address by street/city for customer {customer.id}")
                    return existing_address
                
                # Get or create address with is_primary=False to avoid unique constraint violation
                address, created = Address.objects.get_or_create(
                    customer=customer,
                    legacy_id=f"billing_{address_hash}",
                    defaults={
                        'street': street,
                        'city': city,
                        'postal_code': parsed.get('postal_code', ''),
                        'country': parsed.get('country', 'DE'),
                        'company_name': parsed.get('name', ''),
                        'is_primary': False
                    }
                )
                
                return address
            except Exception as e:
                logger.error(f"Error creating billing address: {e}", exc_info=True)
                
                # Check if the error is due to unique constraint on is_primary
                if "unique_primary_address_per_customer" in str(e):
                    try:
                        # Try to create a non-primary address
                        address = Address.objects.create(
                            customer=customer,
                            legacy_id=f"billing_{address_hash}_non_primary",
                            street=street or "Unknown",
                            city=city or "Unknown",
                            postal_code=parsed.get('postal_code', '00000'),
                            country='DE',
                            company_name=parsed.get('name', ''),
                            is_primary=False
                        )
                        logger.info(f"Created non-primary billing address for customer {customer.id}")
                        return address
                    except Exception as e2:
                        logger.error(f"Failed to create non-primary billing address: {e2}", exc_info=True)
                
                # Fallback: Create a minimal valid address with unique legacy_id
                try:
                    import uuid
                    unique_suffix = str(uuid.uuid4())[:8]
                    address = Address.objects.create(
                        customer=customer,
                        legacy_id=f"billing_{address_hash}_{unique_suffix}",
                        street=street or "Unknown",
                        city=city or "Unknown",
                        postal_code=parsed.get('postal_code', '00000'),
                        country='DE',
                        company_name=parsed.get('name', ''),
                        is_primary=False
                    )
                    logger.info(f"Created fallback billing address for customer {customer.id}")
                    return address
                except Exception as e2:
                    logger.error(f"Fallback address creation failed: {e2}", exc_info=True)
                    return None
        except Exception as e:
            logger.error(f"Error extracting billing address: {e}", exc_info=True)
            return None
    
    def _parse_address(self, address_str: str) -> Dict[str, Any]:
        """Parse address string into structured format."""
        if not address_str:
            return {}
            
        # Clean up the address string
        # Replace literal '\r' with actual line breaks if needed
        if '\\r' in address_str:
            address_str = address_str.replace('\\r', '\n')
        
        # Split address by line breaks (handle different possible formats)
        parts = []
        if '\r' in address_str:
            parts = address_str.split('\r')
        elif '\n' in address_str:
            parts = address_str.split('\n')
        else:
            # Try to split by commas if no line breaks
            parts = address_str.split(',')
        
        # Basic parsing - this would need to be enhanced based on actual data format
        result = {
            'raw': address_str,
            'name': parts[0].strip() if len(parts) > 0 else '',
            'street': parts[1].strip() if len(parts) > 1 else '',
            'city': '',
            'postal_code': '',
            'country': 'DE',  # Default to Germany
        }
        
        # Try to extract postal code and city from the third line
        if len(parts) > 2:
            city_line = parts[2].strip()
            # Look for German postal code pattern (5 digits followed by city name)
            postal_match = re.search(r'(\d{5})\s+(.*)', city_line)
            if postal_match:
                result['postal_code'] = postal_match.group(1)
                result['city'] = postal_match.group(2).strip()
            else:
                result['city'] = city_line
        
        # If we still don't have a postal code, try to find it in any part
        if not result['postal_code']:
            for part in parts:
                postal_match = re.search(r'(\d{5})', part)
                if postal_match:
                    result['postal_code'] = postal_match.group(1)
                    # If we found it in the city line, extract the city
                    if part == city_line:
                        city_text = re.sub(r'\d{5}', '', part).strip()
                        if city_text:
                            result['city'] = city_text
                    break
        
        # Ensure we have at least some values for required fields
        if not result['street'] and len(parts) > 1:
            result['street'] = parts[1].strip()
        
        if not result['city'] and len(parts) > 2:
            result['city'] = parts[2].strip()
        
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
    
    def _get_or_create_customer(self, data: Dict[str, Any]) -> Optional[Any]:
        """Get or create customer from data."""
        try:
            from pyerp.business_modules.sales.models import Customer
            
            customer_id = data.get('KundenNr')
            if not customer_id:
                logger.warning(f"No KundenNr found in record data: {data.get('AbsNr')}")
                return None
            
            # Try to find by legacy_id
            try:
                customer = Customer.objects.get(legacy_id=customer_id)
                logger.info(f"Found customer by legacy_id: {customer_id}")
                return customer
            except Customer.DoesNotExist:
                # Try to find by customer_number
                try:
                    customer = Customer.objects.get(customer_number=str(customer_id))
                    logger.info(f"Found customer by customer_number: {customer_id}")
                    
                    # Update legacy_id if it's not set
                    if not customer.legacy_id:
                        customer.legacy_id = customer_id
                        customer.save(update_fields=['legacy_id'])
                        logger.info(f"Updated customer {customer.id} with legacy_id {customer_id}")
                    
                    return customer
                except Customer.DoesNotExist:
                    # Try to find by legacy_address_number as a fallback
                    try:
                        customer = Customer.objects.get(legacy_address_number=str(customer_id))
                        logger.info(f"Found customer by legacy_address_number: {customer_id}")
                        
                        # Update legacy_id if it's not set
                        if not customer.legacy_id:
                            customer.legacy_id = customer_id
                            customer.save(update_fields=['legacy_id'])
                            logger.info(f"Updated customer {customer.id} with legacy_id {customer_id}")
                        
                        return customer
                    except (Customer.DoesNotExist, AttributeError):
                        # Create a placeholder customer with minimal data
                        name = ""
                        if data.get('Lief_Adr'):
                            parts = data.get('Lief_Adr').split('\r')
                            name = parts[0] if parts else f"Customer {customer_id}"
                        elif data.get('Rech_Adr'):
                            parts = data.get('Rech_Adr').split('\r')
                            name = parts[0] if parts else f"Customer {customer_id}"
                        
                        logger.info(f"Creating new customer with legacy_id {customer_id} and name '{name}'")
                        customer = Customer.objects.create(
                            legacy_id=customer_id,
                            customer_number=str(customer_id),
                            name=name or f"Customer {customer_id}",
                            is_active=True
                        )
                        return customer
        except Exception as e:
            logger.error(f"Error getting or creating customer: {e}", exc_info=True)
            return None 
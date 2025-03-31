"""
Management command to synchronize permissions between the database and a JSON configuration file.
"""

import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from users.models import PermissionCategory, PermissionCategoryItem

CONFIG_PATH = os.path.join('users', 'config', 'permissions_mapping.json')

# Define categories and their patterns for auto-categorization
CATEGORIES = {
    # User & Access Management
    "Users & Access": {
        "patterns": [],
        "icon": "users",
        "order": 10,
        "code": "users",
        "subcategories": {
            "User Management": {
                "patterns": ["auth.user", "users.user"],
                "icon": "user",
                "order": 1,
                "code": "users.user"
            },
            "Group Management": {
                "patterns": ["auth.group"],
                "icon": "users-group",
                "order": 2,
                "code": "users.group"
            },
            "Role Management": {
                "patterns": ["users.role"],
                "icon": "shield",
                "order": 3,
                "code": "users.role"
            },
            "Permission Management": {
                "patterns": ["auth.permission", "users.permissioncategory", "users.permissioncategoryitem"],
                "icon": "key",
                "order": 4,
                "code": "users.permission"
            },
            "Data Access Control": {
                "patterns": ["users.datapermission"],
                "icon": "lock",
                "order": 5,
                "code": "users.datapermission"
            }
        }
    },
    
    # Core Business
    "Warehouse": {
        "patterns": [],
        "icon": "box",
        "order": 20,
        "code": "warehouse",
        "subcategories": {
            "Inventory": {
                "patterns": ["inventory.", "warehouse.inventory"],
                "icon": "package",
                "order": 1,
                "code": "warehouse.inventory"
            },
            "Product": {
                "patterns": ["products.", "product."],
                "icon": "shopping-bag",
                "order": 2,
                "code": "warehouse.product"
            },
            "Stock Management": {
                "patterns": ["stock.", "warehouse.stock"],
                "icon": "layers",
                "order": 3,
                "code": "warehouse.stock"
            }
        }
    },
    
    "Sales": {
        "patterns": [],
        "icon": "shopping-cart",
        "order": 30,
        "code": "sales",
        "subcategories": {
            "Orders": {
                "patterns": ["orders.", "sales.order"],
                "icon": "clipboard",
                "order": 1,
                "code": "sales.orders"
            },
            "Customers": {
                "patterns": ["customers.", "customer."],
                "icon": "users",
                "order": 2,
                "code": "sales.customers"
            },
            "Invoicing": {
                "patterns": ["invoices.", "invoice."],
                "icon": "file-text",
                "order": 3,
                "code": "sales.invoices"
            }
        }
    },
    
    "Purchasing": {
        "patterns": [],
        "icon": "truck",
        "order": 40,
        "code": "purchasing",
        "subcategories": {
            "Purchase Orders": {
                "patterns": ["purchase.", "purchasing.order"],
                "icon": "file",
                "order": 1,
                "code": "purchasing.orders"
            },
            "Suppliers": {
                "patterns": ["suppliers.", "supplier."],
                "icon": "briefcase",
                "order": 2,
                "code": "purchasing.suppliers"
            }
        }
    },
    
    "Production": {
        "patterns": [],
        "icon": "tool",
        "order": 50,
        "code": "production",
        "subcategories": {
            "Manufacturing": {
                "patterns": ["production.", "manufacturing."],
                "icon": "settings",
                "order": 1,
                "code": "production.manufacturing"
            },
            "Quality Control": {
                "patterns": ["quality.", "production.quality"],
                "icon": "check-circle",
                "order": 2,
                "code": "production.quality"
            }
        }
    },
    
    "Finance": {
        "patterns": [],
        "icon": "dollar-sign",
        "order": 60,
        "code": "finance",
        "subcategories": {
            "Accounting": {
                "patterns": ["accounting.", "finance."],
                "icon": "book",
                "order": 1,
                "code": "finance.accounting"
            },
            "Payments": {
                "patterns": ["payments.", "payment."],
                "icon": "credit-card",
                "order": 2,
                "code": "finance.payments"
            }
        }
    },
    
    "System": {
        "patterns": [],
        "icon": "settings",
        "order": 70,
        "code": "system",
        "subcategories": {
            "Configuration": {
                "patterns": ["config.", "configuration.", "settings."],
                "icon": "sliders",
                "order": 1,
                "code": "system.config"
            },
            "Reporting": {
                "patterns": ["reports.", "reporting."],
                "icon": "bar-chart-2",
                "order": 2,
                "code": "system.reports"
            },
            "Notifications": {
                "patterns": ["notifications.", "notification."],
                "icon": "bell",
                "order": 3,
                "code": "system.notifications"
            },
            "Logs": {
                "patterns": ["logs.", "log."],
                "icon": "list",
                "order": 4,
                "code": "system.logs"
            },
            "API": {
                "patterns": ["api.", "external_api."],
                "icon": "code",
                "order": 5,
                "code": "system.api"
            }
        }
    },
    
    # Default
    "Others": {
        "patterns": [],  # Catch-all
        "icon": "layers",
        "order": 999,
        "code": "others",
        "subcategories": {}
    }
}


class Command(BaseCommand):
    help = 'Synchronize permissions between database and JSON configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--export-only',
            action='store_true',
            help='Only export current permissions to JSON, do not import to database',
        )
        parser.add_argument(
            '--import-only',
            action='store_true',
            help='Only import from JSON to database, do not update the JSON file',
        )
        parser.add_argument(
            '--categorize',
            action='store_true',
            help='Automatically categorize permissions in the JSON file',
        )

    def handle(self, *args, **options):
        # Ensure the Others category exists
        others_category, created = PermissionCategory.objects.get_or_create(
            name="Others",
            defaults={
                "description": "Uncategorized permissions",
                "icon": "layers",
                "order": 999,
                "code": "others"
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created default "Others" category'))

        # Handle export unless import-only is specified
        if not options['import_only']:
            self.export_permissions_to_json(others_category)
            
        # Handle categorization if requested
        if options['categorize']:
            self.categorize_permissions()
        
        # Handle import unless export-only is specified
        if not options['export_only']:
            self.import_permissions_from_json()
        
        # Run diff check
        if not options['export_only'] and not options['import_only']:
            self.check_for_new_permissions()

    def export_permissions_to_json(self, default_category):
        """Export all permissions to the JSON file."""
        self.stdout.write("Exporting permissions to JSON...")
        
        # Get existing mapping if file exists
        existing_mapping = {}
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                try:
                    existing_mapping = json.load(f)
                except json.JSONDecodeError:
                    self.stdout.write(self.style.WARNING(
                        f"Error reading {CONFIG_PATH}. Creating new file."))
        
        # Get all permissions from database
        all_permissions = Permission.objects.select_related('content_type').all()
        
        # Create mapping dictionary
        permissions_map = {}
        for permission in all_permissions:
            app_model = f"{permission.content_type.app_label}.{permission.content_type.model}"
            
            # Create unique key for this permission
            perm_key = f"{permission.content_type.app_label}.{permission.codename}"
            
            # Check if this permission is already in the existing mapping
            if perm_key in existing_mapping:
                # Keep the existing category assignment
                permissions_map[perm_key] = existing_mapping[perm_key]
            else:
                # New permission, assign to Others category
                permissions_map[perm_key] = {
                    "id": permission.id,
                    "name": permission.name,
                    "codename": permission.codename,
                    "content_type": app_model,
                    "category": "Others",
                    "subcategory": "",
                    "order": 0
                }
        
        # Write to JSON file
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(permissions_map, f, indent=4, sort_keys=True)
        
        self.stdout.write(self.style.SUCCESS(
            f"Exported {len(permissions_map)} permissions to {CONFIG_PATH}"))

    def categorize_permissions(self):
        """Automatically categorize permissions in the JSON file."""
        self.stdout.write("Categorizing permissions...")
        
        if not os.path.exists(CONFIG_PATH):
            self.stdout.write(self.style.ERROR(f"Config file {CONFIG_PATH} not found"))
            return
            
        # Load the JSON file
        with open(CONFIG_PATH, 'r') as f:
            permissions_map = json.load(f)
            
        # Track which permissions were categorized
        categorized_count = 0
        
        # Categorize permissions
        for perm_key, perm_data in permissions_map.items():
            content_type = perm_data.get('content_type', '')
            
            # Find matching category and subcategory
            category_assigned = False
            
            for category_name, category_info in CATEGORIES.items():
                # Try to match against main category patterns first
                patterns = category_info.get('patterns', [])
                for pattern in patterns:
                    if pattern and (pattern in content_type or pattern in perm_key):
                        permissions_map[perm_key]['category'] = category_name
                        permissions_map[perm_key]['subcategory'] = ""
                        categorized_count += 1
                        category_assigned = True
                        break
                
                # If not matched to main category, try subcategories
                if not category_assigned:
                    subcategories = category_info.get('subcategories', {})
                    for subcategory_name, subcategory_info in subcategories.items():
                        subpatterns = subcategory_info.get('patterns', [])
                        for pattern in subpatterns:
                            if pattern and (pattern in content_type or pattern in perm_key):
                                permissions_map[perm_key]['category'] = category_name
                                permissions_map[perm_key]['subcategory'] = subcategory_name
                                categorized_count += 1
                                category_assigned = True
                                break
                        if category_assigned:
                            break
                            
                if category_assigned:
                    break
                    
            # If no category assigned, keep as "Others"
            if not category_assigned:
                permissions_map[perm_key]['category'] = "Others"
                permissions_map[perm_key]['subcategory'] = ""
        
        # Save the updated mapping
        with open(CONFIG_PATH, 'w') as f:
            json.dump(permissions_map, f, indent=4, sort_keys=True)
            
        self.stdout.write(self.style.SUCCESS(
            f"Categorized {categorized_count} permissions. {len(permissions_map) - categorized_count} remain in 'Others'"
        ))

    def import_permissions_from_json(self):
        """Import permission mappings from JSON to database."""
        self.stdout.write("Importing permissions from JSON to database...")
        
        if not os.path.exists(CONFIG_PATH):
            self.stdout.write(self.style.ERROR(f"Config file {CONFIG_PATH} not found"))
            return
        
        # Load the JSON file
        with open(CONFIG_PATH, 'r') as f:
            permissions_map = json.load(f)
        
        # Create/get the main categories
        main_categories = {}
        subcategories = {}
        
        # Create parent categories first
        for category_name, category_info in CATEGORIES.items():
            defaults = {
                "description": f"Category for {category_name} permissions",
                "icon": category_info.get("icon", "folder"),
                "order": category_info.get("order", 100),
                "code": category_info.get("code", ""),
                "is_subcategory": False,
                "parent": None
            }
            
            category, created = PermissionCategory.objects.update_or_create(
                name=category_name,
                defaults=defaults
            )
            
            main_categories[category_name] = category
            
            if created:
                self.stdout.write(f"Created new main category: {category_name}")
            
            # Create subcategories
            for subcategory_name, subcategory_info in category_info.get('subcategories', {}).items():
                sub_defaults = {
                    "description": f"Subcategory for {subcategory_name} permissions",
                    "icon": subcategory_info.get("icon", "folder"),
                    "order": subcategory_info.get("order", 100),
                    "code": subcategory_info.get("code", ""),
                    "is_subcategory": True,
                    "parent": category
                }
                
                subcategory, sub_created = PermissionCategory.objects.update_or_create(
                    name=subcategory_name,
                    parent=category,
                    defaults=sub_defaults
                )
                
                subcategories[(category_name, subcategory_name)] = subcategory
                
                if sub_created:
                    self.stdout.write(f"Created new subcategory: {category_name} > {subcategory_name}")
        
        # Clear existing mappings if we're doing a full sync
        PermissionCategoryItem.objects.all().delete()
        
        # Create new mappings
        items_to_create = []
        for perm_key, perm_data in permissions_map.items():
            try:
                # Extract app_label and codename
                app_label, codename = perm_key.split('.')
                
                # Get the permission
                permission = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename
                )
                
                # Determine the category
                category_name = perm_data.get('category', 'Others')
                subcategory_name = perm_data.get('subcategory', '')
                
                if subcategory_name and (category_name, subcategory_name) in subcategories:
                    # Use subcategory if defined
                    category = subcategories[(category_name, subcategory_name)]
                else:
                    # Use main category
                    category = main_categories.get(category_name, main_categories['Others'])
                
                order = perm_data.get('order', 0)
                
                item = PermissionCategoryItem(
                    category=category,
                    permission=permission,
                    order=order
                )
                items_to_create.append(item)
                
            except (ValueError, Permission.DoesNotExist) as e:
                self.stdout.write(self.style.WARNING(
                    f"Skipping {perm_key}: {str(e)}"))
        
        # Bulk create for efficiency
        PermissionCategoryItem.objects.bulk_create(items_to_create)
        
        self.stdout.write(self.style.SUCCESS(
            f"Created {len(items_to_create)} permission mappings in database"))

    def check_for_new_permissions(self):
        """Check for permissions in DB that aren't in the JSON file."""
        self.stdout.write("Checking for new permissions...")
        
        # Load existing mapped permissions
        with open(CONFIG_PATH, 'r') as f:
            mapped_permissions = json.load(f)
        
        # Get all permissions from DB
        db_permissions = Permission.objects.select_related('content_type').all()
        
        # Check for permissions in DB not in JSON
        new_permissions = []
        for perm in db_permissions:
            perm_key = f"{perm.content_type.app_label}.{perm.codename}"
            if perm_key not in mapped_permissions:
                new_permissions.append({
                    "key": perm_key,
                    "name": perm.name,
                    "content_type": f"{perm.content_type.app_label}.{perm.content_type.model}"
                })
        
        if new_permissions:
            self.stdout.write(self.style.WARNING(
                f"Found {len(new_permissions)} new permissions not in the mapping file:"))
            for perm in new_permissions:
                self.stdout.write(f"  - {perm['key']} ({perm['name']})")
            self.stdout.write("Run this command again to add them to the mapping file.")
        else:
            self.stdout.write(self.style.SUCCESS("No new permissions found.")) 
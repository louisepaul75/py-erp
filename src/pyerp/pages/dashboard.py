import flet as ft
import uuid
import logging
from ...controls.responsive_layout import ResponsiveGridLayout  # Adjusted import path
from ...widgets.registry import widget_registry
from ...services.layout_service import LayoutService
from ...utils.config import AppConfig

logger = logging.getLogger(__name__)

class DashboardPage(ft.View):
    def __init__(self, page: ft.Page, app_config: AppConfig):
        super().__init__(route="/dashboard")
        self.page = page
        self.app_config = app_config
        self.layout_service = LayoutService(self.app_config)
        self.widgets = {}
        self.edit_mode = False
        self.selected_widget_id = None

        # Create the grid layout first
        self.grid = ResponsiveGridLayout(
            on_resize=self.handle_resize,
            on_widget_select=self.handle_widget_select,
            edit_mode=self.edit_mode,
        )

        # Define Edit Sidebar (replaces NavigationDrawer)
        self.add_widget_dropdown = ft.Dropdown(
            label="Select Widget Type",
            options=[ft.dropdown.Option(key=name) for name in widget_registry.get_widget_names()],
            # width=200 # Removed fixed width to allow expansion
        )
        self.confirm_add_button = ft.ElevatedButton("Add Widget", on_click=self.add_widget_to_cell)
        self.remove_widget_button = ft.ElevatedButton(
            "Remove Selected Widget",
            on_click=self.remove_selected_widget,
            disabled=True # Initially disabled
        )

        self.edit_sidebar = ft.Column(
            [
                ft.Text("Layout Editor", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Divider(),
                ft.Text("Add Widget", style=ft.TextThemeStyle.TITLE_MEDIUM),
                self.add_widget_dropdown,
                self.confirm_add_button,
                ft.Divider(),
                ft.Text("Modify Widget", style=ft.TextThemeStyle.TITLE_MEDIUM),
                self.remove_widget_button,
                # TODO: Add widget configuration options here later
            ],
            width=250, # Give sidebar a fixed width
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            visible=False # Initially hidden
        )

        # Define AppBar Save Button (initially hidden)
        self.save_button = ft.TextButton(
            "Save Layout",
            icon=ft.icons.SAVE,
            on_click=self.save_layout,
            visible=False # Initially hidden
        )

        # Main content row (Sidebar + Grid)
        self.content_row = ft.Row(
            [
                self.edit_sidebar,
                ft.Container( # Wrap grid in a container to allow expansion
                    self.grid,
                    expand=True, # Make grid take remaining space
                    padding=ft.padding.only(left=10) # Add some space when sidebar is visible
                )
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        # AppBar setup
        self.appbar = ft.AppBar(
            title=ft.Text("Dashboard"),
            actions=[
                # Add the save button here
                self.save_button,
                ft.IconButton(
                    icon=ft.icons.EDIT if not self.edit_mode else ft.icons.EDIT_OFF,
                    tooltip="Toggle Edit Mode",
                    on_click=self.toggle_edit_mode,
                ),
                # TODO: Add other actions like refresh, settings?
            ],
        )

        # FAB setup
        self.fab = ft.FloatingActionButton(
            icon=ft.icons.ADD,
            tooltip="Add Widget (Requires Edit Mode)",
            on_click=self.focus_add_widget, # Change FAB to focus add widget in sidebar
            visible=True # Always visible, but action depends on edit mode
        )

        # Assign controls to the View
        self.controls = [self.content_row] # Use the content_row as the main control
        # Removed self.drawer assignment

    async def did_mount_async(self):
        logger.info("DashboardPage mounted. Loading layout.")
        await self.load_layout()
        self.page.update() # Update page after loading

    async def toggle_edit_mode(self, e=None):
        self.edit_mode = not self.edit_mode
        logger.info(f"Toggling edit mode: {'ON' if self.edit_mode else 'OFF'}")
        # Toggle visibility of sidebar and save button
        self.edit_sidebar.visible = self.edit_mode
        self.save_button.visible = self.edit_mode
        self.grid.set_edit_mode(self.edit_mode) # Pass edit mode to grid

        # Update AppBar edit icon
        edit_action = next((a for a in self.appbar.actions if isinstance(a, ft.IconButton) and a.tooltip == "Toggle Edit Mode"), None)
        if edit_action:
            edit_action.icon = ft.icons.EDIT_OFF if self.edit_mode else ft.icons.EDIT

        # Disable remove button if exiting edit mode or no widget selected
        self.remove_widget_button.disabled = not self.edit_mode or self.selected_widget_id is None

        # Adjust FAB visibility/tooltip based on edit mode?
        # self.fab.tooltip = "Add Widget" if self.edit_mode else "Enable Edit Mode to Add Widgets"
        # self.fab.disabled = not self.edit_mode # Maybe disable FAB if not editing? Let's keep it enabled to focus sidebar.

        # Adjust layout spacing/padding if needed
        content_container = self.content_row.controls[1] # Get the grid container
        content_container.padding = ft.padding.only(left=10) if self.edit_mode else ft.padding.all(0)


        # Update the view
        await self.page.update_async(self.appbar, self.content_row, self.remove_widget_button) # Update relevant controls
        logger.debug(f"Edit sidebar visibility: {self.edit_sidebar.visible}")
        logger.debug(f"Save button visibility: {self.save_button.visible}")


    async def focus_add_widget(self, e):
        if not self.edit_mode:
            # If not in edit mode, maybe show a snackbar? Or toggle edit mode?
            # For now, let's just toggle edit mode if FAB is clicked when not editing
            await self.toggle_edit_mode()
            # If toggling on, focus the dropdown
            if self.edit_mode:
                 await self.add_widget_dropdown.focus_async()
        else:
            # If already in edit mode, just focus the dropdown
            await self.add_widget_dropdown.focus_async()
        await self.page.update_async(self.add_widget_dropdown)


    async def handle_widget_select(self, widget_id):
        self.selected_widget_id = widget_id
        logger.info(f"Widget selected in dashboard: {widget_id}")
        # Enable/disable remove button based on selection and edit mode
        self.remove_widget_button.disabled = not self.edit_mode or self.selected_widget_id is None
        await self.page.update_async(self.remove_widget_button) # Only update the button


    async def add_widget_to_cell(self, e):
        widget_type = self.add_widget_dropdown.value
        if not widget_type:
            # TODO: Show error message
            logger.warning("No widget type selected.")
            # Maybe show a snackbar
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Please select a widget type first!"), open=True))
            await self.page.update_async()
            return

        # Generate a unique ID for the new widget
        widget_id = str(uuid.uuid4())
        logger.info(f"Attempting to add widget of type '{widget_type}' with id '{widget_id}'")

        # Create the widget instance using the registry
        widget_instance_data = widget_registry.create_widget(widget_type, widget_id, self.page, self.app_config)
        if not widget_instance_data:
             logger.error(f"Failed to create widget instance for type '{widget_type}'")
             self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error creating widget '{widget_type}'"), open=True))
             await self.page.update_async()
             return

        widget_instance = widget_instance_data["control"]
        default_config = widget_instance_data["default_config"]

        # Add to the grid (let grid find the first empty cell)
        added_successfully = self.grid.add_widget(widget_instance)

        if added_successfully:
            self.widgets[widget_id] = {
                "instance": widget_instance,
                "type": widget_type,
                "config": default_config # Store default config initially
            }
            logger.info(f"Widget '{widget_id}' ({widget_type}) added to grid and internal tracking.")
            # Reset dropdown?
            # self.add_widget_dropdown.value = None
        else:
            logger.warning(f"Failed to add widget '{widget_id}' ({widget_type}) to the grid (maybe no space?).")
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Could not add widget. Grid might be full."), open=True))

        await self.page.update_async() # Update the whole page/grid


    async def remove_selected_widget(self, e):
        if not self.selected_widget_id:
            logger.warning("Remove clicked but no widget selected.")
            return

        widget_id_to_remove = self.selected_widget_id
        logger.info(f"Attempting to remove widget: {widget_id_to_remove}")

        # Remove from grid
        removed_from_grid = self.grid.remove_widget(widget_id_to_remove)

        if removed_from_grid:
             # Remove from internal tracking
            if widget_id_to_remove in self.widgets:
                del self.widgets[widget_id_to_remove]
                logger.info(f"Widget {widget_id_to_remove} removed from internal tracking.")
            else:
                logger.warning(f"Widget {widget_id_to_remove} was removed from grid but not found in internal tracking.")

            self.selected_widget_id = None # Clear selection
            self.remove_widget_button.disabled = True # Disable button again
            await self.page.update_async() # Update the view
        else:
            logger.warning(f"Failed to remove widget {widget_id_to_remove} from the grid.")
            # Maybe show a snackbar?
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Could not remove widget {widget_id_to_remove}."), open=True))
            await self.page.update_async(self.remove_widget_button) # Update button state if needed


    async def save_layout(self, e=None):
        logger.info("Saving dashboard layout...")
        current_layout = self.grid.get_layout_config()
        # Also include widget configurations
        for item in current_layout:
            widget_id = item.get("i")
            if widget_id in self.widgets:
                # If the widget has a get_config method, use it
                widget_instance = self.widgets[widget_id]["instance"]
                config = {}
                if hasattr(widget_instance, 'get_config') and callable(widget_instance.get_config):
                    try:
                        config = await widget_instance.get_config()
                        logger.debug(f"Retrieved config for widget {widget_id}: {config}")
                    except Exception as exc:
                        logger.error(f"Error getting config for widget {widget_id}: {exc}", exc_info=True)
                        config = self.widgets[widget_id].get("config", {}) # Fallback to stored config
                else:
                     config = self.widgets[widget_id].get("config", {}) # Fallback if no method

                item['widget_type'] = self.widgets[widget_id]['type']
                item['config'] = config # Add config to the layout item
            else:
                logger.warning(f"Widget ID {widget_id} found in grid layout but not in internal widget tracking during save.")


        try:
            await self.layout_service.save_layout('dashboard', current_layout)
            logger.info("Dashboard layout saved successfully.")
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Layout Saved!"), open=True))
            # Maybe exit edit mode after saving?
            if self.edit_mode:
                await self.toggle_edit_mode()
            else:
                await self.page.update_async()
        except Exception as ex:
            logger.error(f"Error saving dashboard layout: {ex}", exc_info=True)
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error saving layout: {ex}"), open=True))
            await self.page.update_async()


    async def load_layout(self):
        logger.info("Loading dashboard layout...")
        try:
            layout_data = await self.layout_service.load_layout('dashboard')
            if layout_data:
                logger.info(f"Layout data loaded: {len(layout_data)} items")
                # Clear existing widgets from grid and tracking before loading
                self.grid.clear_widgets()
                self.widgets.clear()
                self.selected_widget_id = None
                self.remove_widget_button.disabled = True

                widget_instances = []
                layout_config = []
                for item in layout_data:
                    widget_id = item.get("i")
                    widget_type = item.get("widget_type")
                    config = item.get("config", {}) # Load config if available
                    if not widget_id or not widget_type:
                        logger.warning(f"Skipping layout item due to missing 'i' or 'widget_type': {item}")
                        continue

                    logger.debug(f"Loading widget: id={widget_id}, type={widget_type}, config={config}")
                    # Create widget instance using registry
                    widget_instance_data = widget_registry.create_widget(widget_type, widget_id, self.page, self.app_config, initial_config=config)
                    if not widget_instance_data:
                         logger.error(f"Failed to create widget instance for type '{widget_type}' during layout load.")
                         continue # Skip this widget if creation fails

                    widget_instance = widget_instance_data["control"]

                    # Add to internal tracking
                    self.widgets[widget_id] = {
                        "instance": widget_instance,
                        "type": widget_type,
                        "config": config # Store loaded config
                    }
                    # Prepare for grid update
                    widget_instances.append(widget_instance)
                    # Keep layout config separate
                    layout_config.append({k: v for k, v in item.items() if k not in ['widget_type', 'config']}) # Pass only RGL keys

                logger.debug(f"Prepared {len(widget_instances)} widgets and {len(layout_config)} layout items for grid.")
                # Update grid with all widgets and the layout configuration
                self.grid.update_layout(layout_config, widget_instances)
                logger.info("Grid updated with loaded layout and widgets.")
            else:
                logger.info("No saved layout found for dashboard. Starting with empty layout.")
                self.grid.clear_widgets()
                self.widgets.clear()

        except Exception as ex:
            logger.error(f"Error loading dashboard layout: {ex}", exc_info=True)
            # Handle error, maybe load a default layout or show an error message
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Error loading layout: {ex}. Starting fresh."), open=True))
            self.grid.clear_widgets()
            self.widgets.clear()

        # Ensure UI state is consistent after load
        self.selected_widget_id = None
        self.remove_widget_button.disabled = not self.edit_mode # Should be disabled if not in edit mode
        await self.page.update_async()


    async def handle_resize(self, width, height, breakpoint_name):
        # This might be needed if grid content needs explicit updating on resize
        # logger.debug(f"Dashboard Resized: w={width}, h={height}, bp={breakpoint_name}")
        # await self.page.update_async(self.grid) # Avoid full page update if possible
        pass

    # Override build method if needed, otherwise __init__ sets up controls
    # def build(self):
    #     # This method is implicitly called by Flet View.
    #     # The controls are already defined in __init__.
    #     pass

</rewritten_file> 
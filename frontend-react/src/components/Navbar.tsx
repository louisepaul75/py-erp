"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import {
  Sun,
  Moon,
  Settings,
  LogOut,
  ChevronDown,
  User,
  Palette,
  Package,
  Paintbrush,
  Bell,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "next-themes";
import LanguageSelector from "./LanguageSelector";
import { useLogout } from "@/lib/auth/authHooks";
import useAppTranslation from "@/hooks/useTranslationWrapper";
import { useIsAuthenticated } from "@/lib/auth/authHooks";
import { MobileMenu } from "./MobileMenu";
import { useScreenSize } from "@/utils/responsive";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem as ShadcnDropdownMenuItem,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from "@/components/ui/dropdown-menu";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import { useNotifications } from "@/hooks/useNotifications";
import { Button } from "@/components/ui/button";
import { NotificationItem } from "@/components/notifications/NotificationItem";
import { useQueryClient } from "@tanstack/react-query";

function DropdownItem({
  children,
  href,
  onClick,
}: {
  children: React.ReactNode;
  href?: string;
  onClick?: () => void;
}) {
  if (href) {
    return (
      <Link
        href={href}
        className="block px-4 py-2 text-sm text-popover-foreground hover:bg-accent hover:text-accent-foreground flex items-center"
        role="menuitem"
      >
        {children}
      </Link>
    );
  }

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left block px-4 py-2 text-sm text-popover-foreground",
        "hover:bg-accent hover:text-accent-foreground flex items-center"
      )}
      role="menuitem"
    >
      {children}
    </button>
  );
}

export function Navbar() {
  const [testMenuOpen, setTestMenuOpen] = useState(false);
  const { theme, setTheme } = useTheme();
  const { t } = useAppTranslation();
  const { user } = useIsAuthenticated();
  const logout = useLogout();
  const { isMobile, isTablet } = useScreenSize();
  const queryClient = useQueryClient();
  const { 
    unreadCount, 
    notifications, 
    isLoadingUnreadCount, 
    markAsRead,
    refetchNotifications,
    refetchUnreadCount 
  } = useNotifications({ is_read: false, limit: 5 });

  // Debug logs
  useEffect(() => {
    console.log("Unread count:", unreadCount);
    console.log("Notifications:", notifications);
    console.log("Is loading:", isLoadingUnreadCount);
  }, [unreadCount, notifications, isLoadingUnreadCount]);

  // Function to refresh notification data with cache reset
  const refreshNotifications = () => {
    console.log("Manually refreshing notification data...");
    // Clear all notification-related caches
    queryClient.invalidateQueries({ queryKey: ['notifications'] });
    // Then refetch the data
    refetchNotifications();
    refetchUnreadCount();
  };

  const toggleTestDropdown = () => setTestMenuOpen(!testMenuOpen);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const testDropdown = document.getElementById("test-dropdown");

      if (testDropdown && !testDropdown.contains(event.target as Node)) {
        setTestMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    logout.mutate();
  };

  const navigationItems = [
    { href: "/dashboard", label: t("navigation.home") },
    { href: "/products", label: t("navigation.products") },
    // { href: '/production', label: t('navigation.production') },
  ];

  return (
    <nav className="bg-header text-header-foreground shadow-md fixed w-full z-50">
      <div className="max-w-full mx-0 px-2 sm:px-3 lg:px-4">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center pl-2">
            <Link href="/dashboard">
              <Image
                src="/wsz_logo_long.png"
                alt="Wilhelm Schweizer Zinnmanufaktur"
                width={200}
                height={50}
                className="h-10 w-auto"
              />
            </Link>
          </div>

          {/* Mobile menu */}
          <div className="flex items-center lg:hidden">
            <MobileMenu
              items={user ? [
                ...navigationItems,
                { href: "/warehouse", label: t("navigation.inventory") },
                { href: "/picklist", label: "Picklist" },
              ] : [
                { href: "/dashboard", label: t("navigation.home") }
              ]}
            />
          </div>

          {/* Navigation Links - Desktop */}
          {user && (
            <div className="hidden lg:flex items-center justify-center flex-1">
              <div className="flex space-x-4">
                {navigationItems.map((item) => (
                  <NavLink key={item.href} href={item.href} label={item.label} />
                ))}

                {/* Add Sales Dropdown */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button className="px-3 py-2 rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground flex items-center">
                      <span>{t("navigation.sales")}</span>
                      <ChevronDown className="ml-1 h-4 w-4 text-current" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <ShadcnDropdownMenuItem asChild>
                      <Link href="/sales" className="flex items-center">
                        {t("navigation.sales_dashboard")}
                      </Link>
                    </ShadcnDropdownMenuItem>
                    <ShadcnDropdownMenuItem asChild>
                      <Link href="/sales/customers" className="flex items-center">
                        {t("navigation.customers")}
                      </Link>
                    </ShadcnDropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                {/*  Production dropdown */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button className="px-3 py-2 rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground flex items-center">
                      <span>{t("navigation.production")}</span>
                      <ChevronDown className="ml-1 h-4 w-4 text-current" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <ShadcnDropdownMenuItem asChild>
                      <Link href="/production" className="flex items-center">
                        {t("navigation.production")}
                      </Link>
                    </ShadcnDropdownMenuItem>
                    <ShadcnDropdownMenuItem asChild>
                      <Link href="/mold-management" className="flex items-center">
                        {t("navigation.mold_management")}
                      </Link>
                    </ShadcnDropdownMenuItem>
                    <ShadcnDropdownMenuItem asChild>
                      <Link href="/production/casting" className="flex items-center">
                        Casting Manager
                      </Link>
                    </ShadcnDropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                {/* Inventory Dropdown */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button className="px-3 py-2 rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground flex items-center">
                      <Package className="h-4 w-4 mr-2 text-current" />
                      <span>{t("navigation.inventory")}</span>
                      <ChevronDown className="ml-1 h-4 w-4 text-current" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <ShadcnDropdownMenuItem asChild>
                      <Link href="/warehouse" className="flex items-center">
                        Warehouse Management
                      </Link>
                    </ShadcnDropdownMenuItem>
                    <ShadcnDropdownMenuItem asChild>
                      <Link href="/picklist" className="flex items-center">
                        Picklist
                      </Link>
                    </ShadcnDropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                {/* Test dropdown */}
                <div className="relative" id="test-dropdown">
                  <button
                    onClick={toggleTestDropdown}
                    className="px-3 py-2 rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground flex items-center"
                  >
                    <span>Test</span>
                    <ChevronDown className="ml-1 h-4 w-4 text-current" />
                  </button>

                  {testMenuOpen && (
                    <div className="absolute left-0 mt-2 w-56 rounded-md shadow-lg bg-popover text-popover-foreground ring-1 ring-border ring-opacity-5 focus:outline-none z-50">
                      <div
                        className="py-1"
                        role="menu"
                        aria-orientation="vertical"
                      >
                        <DropdownItem href="/ui-components">
                          <Palette className="mr-3 h-5 w-5" />
                          UI Components / Style Guide
                        </DropdownItem>
                        <DropdownItem href="/test/feature1">
                          Feature 1
                        </DropdownItem>
                        <DropdownItem href="/test/feature2">
                          Feature 2
                        </DropdownItem>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Right side icons (Theme, Language, Notifications, User Menu) - Desktop */}
          <div className="hidden lg:flex items-center space-x-3 pr-2">
            {/* Notification Popover */}
            {user && (
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="relative rounded-full"
                    aria-label={`${unreadCount} unread notifications`}
                    onClick={refreshNotifications}
                  >
                    <Bell className="h-6 w-6" />
                    {unreadCount > 0 && (
                      <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                        {unreadCount > 9 ? "9+" : unreadCount}
                      </span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-80 p-0" align="end">
                  <div className="p-4 font-medium border-b">
                    Notifications
                  </div>
                  <div className="max-h-[300px] overflow-y-auto">
                    {isLoadingUnreadCount ? (
                      <div className="p-4 text-sm text-muted-foreground">Loading notifications...</div>
                    ) : notifications && notifications.length > 0 ? (
                      <div className="divide-y">
                        {notifications.slice(0, 5).map((notification) => (
                          <NotificationItem
                            key={notification.id}
                            notification={notification}
                            onMarkAsRead={markAsRead}
                            isMarkingRead={false}
                          />
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 text-sm text-muted-foreground">
                        <p>No new notifications</p>
                        <p className="text-xs mt-2">Debug info:</p>
                        <pre className="text-xs mt-1 bg-muted p-2 rounded overflow-x-auto">
                          {JSON.stringify({
                            unreadCount,
                            notificationsLength: notifications?.length || 0,
                            isLoading: isLoadingUnreadCount
                          }, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                  <div className="p-2 border-t text-center">
                    <Link href="/notifications" className="text-primary hover:underline text-sm">
                      View all notifications
                    </Link>
                  </div>
                </PopoverContent>
              </Popover>
            )}

            {/* User Menu - Desktop */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  type="button"
                  className="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ring items-center bg-muted/20 border border-border px-3 py-1.5"
                  id="user-menu"
                >
                  <span className="sr-only">Open user menu</span>
                  <span className="mr-2">
                    {user?.username || "Guest"}
                  </span>
                  <User className="h-8 w-8 rounded-full p-1 bg-muted text-muted-foreground" />
                  <ChevronDown className="ml-1 h-4 w-4 text-current" />
                </button>
              </DropdownMenuTrigger>

              <DropdownMenuContent
                align="end"
                className="w-48"
              >
                <DropdownMenuSub>
                  <DropdownMenuSubTrigger className="flex items-center w-full text-left px-2 py-1.5 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground">
                    <Paintbrush className="mr-2 h-4 w-4" />
                    <span>Change Theme</span>
                  </DropdownMenuSubTrigger>
                  <DropdownMenuSubContent>
                    <ShadcnDropdownMenuItem onClick={() => setTheme('default-light')}>
                      Light
                    </ShadcnDropdownMenuItem>
                    <ShadcnDropdownMenuItem onClick={() => setTheme('default-dark')}>
                      Dark
                    </ShadcnDropdownMenuItem>
                    <ShadcnDropdownMenuItem onClick={() => setTheme('matsu-light')}>
                      Cartoon
                    </ShadcnDropdownMenuItem>
                  </DropdownMenuSubContent>
                </DropdownMenuSub>

                <div className="px-2 py-1.5 text-sm text-muted-foreground">
                  <LanguageSelector />
                </div>

                <ShadcnDropdownMenuItem asChild>
                  <Link href="/settings" className="flex items-center w-full">
                    <Settings className="mr-2 h-4 w-4" />
                    <span>
                      {user?.isAdmin
                        ? t("navigation.admin_settings")
                        : t("navigation.settings")}
                    </span>
                  </Link>
                </ShadcnDropdownMenuItem>

                <ShadcnDropdownMenuItem onClick={handleLogout} className="flex items-center w-full">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Logout</span>
                </ShadcnDropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Right side icons (Notifications, User Menu) - Mobile */}
          <div className="lg:hidden flex items-center space-x-2">
            {/* Notification Popover - Mobile */}
            {user && (
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="relative rounded-full"
                    aria-label={`${unreadCount} unread notifications`}
                    onClick={refreshNotifications}
                  >
                    <Bell className="h-6 w-6" />
                    {unreadCount > 0 && (
                      <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 transform translate-x-1/2 -translatey-1/2 bg-red-600 rounded-full">
                        {unreadCount > 9 ? "9+" : unreadCount}
                      </span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-80 p-0" align="end">
                  <div className="p-4 font-medium border-b">
                    Notifications
                  </div>
                  <div className="max-h-[300px] overflow-y-auto">
                    {isLoadingUnreadCount ? (
                      <div className="p-4 text-sm text-muted-foreground">Loading notifications...</div>
                    ) : notifications && notifications.length > 0 ? (
                      <div className="divide-y">
                        {notifications.slice(0, 5).map((notification) => (
                          <NotificationItem
                            key={notification.id}
                            notification={notification}
                            onMarkAsRead={markAsRead}
                            isMarkingRead={false}
                          />
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 text-sm text-muted-foreground">
                        <p>No new notifications</p>
                        <p className="text-xs mt-2">Debug info:</p>
                        <pre className="text-xs mt-1 bg-muted p-2 rounded overflow-x-auto">
                          {JSON.stringify({
                            unreadCount,
                            notificationsLength: notifications?.length || 0,
                            isLoading: isLoadingUnreadCount
                          }, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                  <div className="p-2 border-t text-center">
                    <Link href="/notifications" className="text-primary hover:underline text-sm">
                      View all notifications
                    </Link>
                  </div>
                </PopoverContent>
              </Popover>
            )}

            {/* Mobile user button */}
            <DropdownMenu>
              <div className="flex items-center">
                <div className="relative ml-3" id="mobile-user-dropdown">
                  <DropdownMenuTrigger asChild>
                    <button
                      type="button"
                      className="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ring bg-muted/20 border border-border p-1"
                    >
                      <User className="h-8 w-8 rounded-full p-1 bg-muted text-muted-foreground" />
                    </button>
                  </DropdownMenuTrigger>

                  <DropdownMenuContent
                    align="end"
                    className="w-48"
                  >
                    <DropdownMenuSub>
                      <DropdownMenuSubTrigger className="flex items-center w-full text-left px-2 py-1.5 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground">
                        <Paintbrush className="mr-2 h-4 w-4" />
                        <span>Change Theme</span>
                      </DropdownMenuSubTrigger>
                      <DropdownMenuSubContent>
                        <ShadcnDropdownMenuItem onClick={() => setTheme('default-light')}>
                          Light
                        </ShadcnDropdownMenuItem>
                        <ShadcnDropdownMenuItem onClick={() => setTheme('default-dark')}>
                          Dark
                        </ShadcnDropdownMenuItem>
                        <ShadcnDropdownMenuItem onClick={() => setTheme('matsu-light')}>
                          Cartoon
                        </ShadcnDropdownMenuItem>
                      </DropdownMenuSubContent>
                    </DropdownMenuSub>

                    <div className="px-2 py-1.5 text-sm text-muted-foreground">
                      <LanguageSelector />
                    </div>

                    <ShadcnDropdownMenuItem asChild>
                      <Link href="/settings" className="flex items-center w-full">
                        <Settings className="mr-2 h-4 w-4" />
                        <span>{t("navigation.settings")}</span>
                      </Link>
                    </ShadcnDropdownMenuItem>

                    <ShadcnDropdownMenuItem onClick={handleLogout} className="flex items-center w-full">
                      <LogOut className="mr-2 h-4 w-4" />
                      <span>Logout</span>
                    </ShadcnDropdownMenuItem>
                  </DropdownMenuContent>
                </div>
              </div>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </nav>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="px-3 py-2 rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground"
    >
      {label}
    </Link>
  );
}

export default Navbar;

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
    { href: "/sales", label: t("navigation.sales") },
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
              items={[
                ...navigationItems,
                { href: "/warehouse", label: t("navigation.inventory") },
                { href: "/picklist", label: "Picklist" },
              ]}
            />
          </div>

          {/* Navigation Links - Desktop */}
          <div className="hidden lg:flex items-center justify-center flex-1">
            <div className="flex space-x-4">
              {navigationItems.map((item) => (
                <NavLink key={item.href} href={item.href} label={item.label} />
              ))}

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

          {/* User Menu - Desktop - Refactored with Shadcn DropdownMenu */}
          <div className="hidden lg:flex items-center pr-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  type="button"
                  className="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ring items-center"
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

          {/* Mobile user button - Refactored with Shadcn DropdownMenu */}
          {(isMobile || isTablet) && (
            <DropdownMenu>
              <div className="flex items-center">
                <div className="relative ml-3" id="mobile-user-dropdown">
                  <DropdownMenuTrigger asChild>
                    <button
                      type="button"
                      className="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ring"
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
          )}
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

// components/ProductList.tsx
import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Search,
  X,
  Filter,
  ArrowUpDown,
  Sliders,
  Inbox,
  Tag,
  Bookmark,
} from "lucide-react";

interface Product {
  nummer: string;
  bezeichnung: string;
  status: string;
}

interface ProductListProps {
  showSidebar: boolean;
  searchTerm: string;
  setSearchTerm: (value: string) => void;
  filteredProducts: Product[];
  selectedItem: string | null;
  setSelectedItem: (value: string) => void;
}

export default function ProductList({
  showSidebar,
  searchTerm,
  setSearchTerm,
  filteredProducts,
  selectedItem,
  setSelectedItem,
}: ProductListProps) {
  const [sortField, setSortField] = useState<keyof Product>("nummer");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50";
      case "inactive":
        return "bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400 border-amber-200 dark:border-amber-900/50";
      case "draft":
        return "bg-slate-50 text-slate-700 dark:bg-slate-800/50 dark:text-slate-400 border-slate-200 dark:border-slate-700";
      default:
        return "bg-slate-50 text-slate-700 dark:bg-slate-800/50 dark:text-slate-400 border-slate-200 dark:border-slate-700";
    }
  };

  const sortedFilteredProducts = useMemo(() => {
    return [...filteredProducts].sort((a, b) => {
      if (a[sortField] < b[sortField]) return sortOrder === "asc" ? -1 : 1;
      if (a[sortField] > b[sortField]) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
  }, [filteredProducts, sortField, sortOrder]);

  const handleSort = (field: keyof Product) => {
    setSortField(field);
    setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
  };

  return (
    <div className="w-full md:w-80 lg:w-96 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col">
      {/* Search and Filters */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
        <div className="relative md:hidden mb-4">
          <Input
            className="w-full pl-9 h-10 rounded-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus-visible:ring-blue-500"
            placeholder="Suchen..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <div className="absolute left-3 top-1/2 -translate-y-1/2">
            <Search className="h-4 w-4 text-slate-400" />
          </div>
          {searchTerm && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full"
              onClick={() => setSearchTerm("")}
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium text-slate-900 dark:text-slate-100">
            Produkte
          </h2>
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full"
            >
              <Filter className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full"
            >
              <ArrowUpDown className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full"
            >
              <Sliders className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Product List */}
      <div className="flex-1 overflow-auto">
        {filteredProducts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-4 text-center">
            <Inbox className="h-12 w-12 text-slate-300 dark:text-slate-600 mb-2" />
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Keine Produkte gefunden
            </p>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
              Versuchen Sie, Ihre Suchkriterien zu ändern
            </p>
          </div>
        ) : (
          <div className="p-2">
            <div className="grid grid-cols-[auto_1fr_auto] gap-2 font-medium text-sm text-slate-500 dark:text-slate-400 p-2 bg-slate-50 dark:bg-slate-800/50 rounded-t-lg">
              <div
                className="cursor-pointer"
                onClick={() => handleSort("nummer")}
              >
                Nummer
                {sortField === "nummer" && (
                  <span>{sortOrder === "asc" ? " ↑" : " ↓"}</span>
                )}
              </div>
              <div
                className="cursor-pointer"
                onClick={() => handleSort("bezeichnung")}
              >
                Bezeichnung
                {sortField === "bezeichnung" && (
                  <span>{sortOrder === "asc" ? " ↑" : " ↓"}</span>
                )}
              </div>
              <div
                className="text-center cursor-pointer"
                onClick={() => handleSort("status")}
              >
                Status
                {sortField === "status" && (
                  <span>{sortOrder === "asc" ? " ↑" : " ↓"}</span>
                )}
              </div>
            </div>
            {sortedFilteredProducts.map((product) => (
              <div
                key={product.nummer}
                className={`p-3 my-1 rounded-xl cursor-pointer transition-all ${
                  selectedItem === product.nummer
                    ? "bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500"
                    : "hover:bg-slate-50 dark:hover:bg-slate-800/50 border-l-4 border-transparent"
                }`}
                onClick={() => setSelectedItem(product.nummer)}
              >
                <div className="grid grid-cols-[auto_1fr_auto] gap-2 items-center">
                  <div className="font-medium">{product.nummer}</div>
                  <div className="text-sm text-slate-500 dark:text-slate-400 truncate">
                    {product.bezeichnung || "—"}
                  </div>
                  <div className="text-center">
                    <Badge
                      variant="outline"
                      className={`text-xs px-2 py-0 h-5 ${getStatusColor(
                        product.status
                      )}`}
                    >
                      {product.status === "active"
                        ? "Aktiv"
                        : product.status === "inactive"
                        ? "Inaktiv"
                        : "Entwurf"}
                    </Badge>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <Badge
                    variant="secondary"
                    className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                  >
                    <Tag className="h-3 w-3 mr-1" />
                    Zinnfigur
                  </Badge>
                  <Badge
                    variant="secondary"
                    className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                  >
                    <Bookmark className="h-3 w-3 mr-1" />
                    Eisenbahn
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

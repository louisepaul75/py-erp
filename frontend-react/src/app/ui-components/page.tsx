'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { 
  Search, 
  Filter, 
  BarChart4, 
  PieChart, 
  LineChart, 
  Plus, 
  Trash, 
  Edit, 
  Save, 
  Download, 
  Upload, 
  RefreshCw,
  Settings,
  ChevronDown,
  ChevronUp,
  ArrowUpDown,
  X,
  Check,
  User,
  Home,
  ShoppingCart,
  FileText,
  Bell,
  Calendar,
  Mail,
  Phone,
  CreditCard,
  HelpCircle,
  Info,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';

// Import our enhanced components
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Input,
  StatusBadge,
  Badge
} from '@/components/ui';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'; // Added import
import { themeColors } from '@/lib/theme-config';

// Import Recharts components
import {
  LineChart as RechartsLineChart,
  Line,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Scatter,
  ScatterChart,
  Cell
} from 'recharts';

import { SkinnyTable } from "@/components/ui/skinny-table";

// Import table components
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  TableCaption,
} from '@/components/ui/table';

// Sample data for charts
const lineData = [
  { name: 'Jan', value: 400 },
  { name: 'Feb', value: 600 },
  { name: 'Mar', value: 300 },
  { name: 'Apr', value: 200 },
  { name: 'May', value: 450 },
  { name: 'Jun', value: 500 },
];

const barData = [
  { name: 'Q1', value: 2400 },
  { name: 'Q2', value: 1398 },
  { name: 'Q3', value: 9800 },
  { name: 'Q4', value: 3908 },
];

const pieData = [
  { name: 'Group A', value: 400 },
  { name: 'Group B', value: 300 },
  { name: 'Group C', value: 300 },
  { name: 'Group D', value: 200 },
];

const areaData = [
  { name: 'Jan', value: 400 },
  { name: 'Feb', value: 600 },
  { name: 'Mar', value: 300 },
  { name: 'Apr', value: 200 },
  { name: 'May', value: 450 },
  { name: 'Jun', value: 500 },
];

const radarData = [
  { subject: 'Math', A: 120, B: 110, fullMark: 150 },
  { subject: 'English', A: 98, B: 130, fullMark: 150 },
  { subject: 'Geography', A: 86, B: 130, fullMark: 150 },
  { subject: 'Physics', A: 99, B: 100, fullMark: 150 },
  { subject: 'History', A: 85, B: 90, fullMark: 150 },
];

const scatterData = [
  { x: 100, y: 200, z: 200 },
  { x: 120, y: 100, z: 260 },
  { x: 170, y: 300, z: 400 },
  { x: 140, y: 250, z: 280 },
  { x: 150, y: 400, z: 500 },
  { x: 110, y: 280, z: 200 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

// Define the semantic colors based on CSS variables in globals.css
const colorCategories = [
  {
    category: "Text Colors",
    colors: [
      { name: "Foreground", variable: "--foreground" },
      { name: "Muted Foreground", variable: "--muted-foreground" },
      { name: "Primary Foreground", variable: "--primary-foreground" },
      { name: "Secondary Foreground", variable: "--secondary-foreground" },
      { name: "Accent Foreground", variable: "--accent-foreground" },
      { name: "Destructive Foreground", variable: "--destructive-foreground" },
      { name: "Card Foreground", variable: "--card-foreground" },
      { name: "Popover Foreground", variable: "--popover-foreground" },
    ]
  },
  {
    category: "Background Colors",
    colors: [
      { name: "Background", variable: "--background" },
      { name: "Card", variable: "--card" },
      { name: "Popover", variable: "--popover" },
      { name: "Muted", variable: "--muted" },
    ]
  },
  {
    category: "Layout Colors",
    colors: [
      { name: "Header Background", variable: "--header-background" },
      { name: "Header Foreground", variable: "--header-foreground" },
      { name: "Footer Background", variable: "--footer-background" },
      { name: "Footer Foreground", variable: "--footer-foreground" },
      { name: "Sidebar Background", variable: "--sidebar-background" },
      { name: "Sidebar Foreground", variable: "--sidebar-foreground" },
    ]
  },
  {
    category: "Brand Colors",
    colors: [
      { name: "Primary", variable: "--primary" },
      { name: "Secondary", variable: "--secondary" },
      { name: "Accent", variable: "--accent" },
    ]
  },
  {
    category: "UI Element Colors",
    colors: [
      { name: "Border", variable: "--border" },
      { name: "Input", variable: "--input" },
      { name: "Ring", variable: "--ring" },
      { name: "Destructive", variable: "--destructive" },
    ]
  },
  {
    category: "Status Colors",
    colors: [
      { name: "Status Success", variable: "--status-success" },
      { name: "Status Success Foreground", variable: "--status-success-foreground" },
      { name: "Status Warning", variable: "--status-warning" },
      { name: "Status Warning Foreground", variable: "--status-warning-foreground" },
      { name: "Status Error", variable: "--status-error" },
      { name: "Status Error Foreground", variable: "--status-error-foreground" },
    ]
  }
];

// Flat list for backward compatibility if needed elsewhere
const semanticColors = colorCategories.flatMap(category => category.colors);

// Define the status colors based on CSS variables
const statusColors = colorCategories.find(c => c.category === "Status Colors")?.colors || [];

export default function UIComponentsPage() {
  const [activeTab, setActiveTab] = useState('buttons');

  return (
    <div className="container mx-auto py-20 px-4 md:px-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-primary">UI Components / Style Guide</h1>
        <p className="text-muted-foreground mb-8">A collection of UI components for the pyERP system</p>

        <Tabs defaultValue="buttons" className="w-full" onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 mb-8">
            <TabsTrigger value="buttons">Buttons</TabsTrigger>
            <TabsTrigger value="inputs">Inputs</TabsTrigger>
            <TabsTrigger value="cards">Cards</TabsTrigger>
            <TabsTrigger value="tables">Tables</TabsTrigger>
            <TabsTrigger value="charts">Charts</TabsTrigger>
            <TabsTrigger value="filters">Filters</TabsTrigger>
            <TabsTrigger value="icons">Icons</TabsTrigger>
            <TabsTrigger value="colors">Colors</TabsTrigger>
          </TabsList>

          {/* Buttons Section */}
          <TabsContent value="buttons" className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>Buttons</CardTitle>
                <CardDescription>Button styles for different actions and states</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Primary</h3>
                    <div className="flex flex-wrap gap-2">
                      <Button>Default</Button>
                      <Button size="sm">Small</Button>
                      <Button disabled>Disabled</Button>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Secondary</h3>
                    <div className="flex flex-wrap gap-2">
                      <Button variant="secondary">Default</Button>
                      <Button variant="secondary" size="sm">Small</Button>
                      <Button variant="secondary" disabled>Disabled</Button>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Outline</h3>
                    <div className="flex flex-wrap gap-2">
                      <Button variant="outline">Default</Button>
                      <Button variant="outline" size="sm">Small</Button>
                      <Button variant="outline" disabled>Disabled</Button>
                    </div>
                  </div>
                </div>

                <Separator className="my-6" />

                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Icon Buttons</h3>
                  <div className="flex flex-wrap gap-2">
                    <Button icon={Plus}>Add</Button>
                    <Button variant="secondary" icon={Edit}>Edit</Button>
                    <Button variant="outline" icon={Trash}>Delete</Button>
                    <Button icon={Save}>Save</Button>
                    <Button variant="secondary" icon={Download}>Download</Button>
                    <Button variant="outline" icon={Upload}>Upload</Button>
                    <Button size="icon" icon={RefreshCw} aria-label="Refresh" />
                  </div>
                </div>

                <Separator className="my-6" />

                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Loading State</h3>
                  <div className="flex flex-wrap gap-2">
                    <Button loading>Loading</Button>
                    <Button variant="secondary" loading>Processing</Button>
                    <Button variant="outline" loading>Saving</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Destructive Action</CardTitle>
                <CardDescription>Button for actions that cannot be easily undone</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  <Button variant="destructive">Delete Permanently</Button>
                  <Button variant="destructive" icon={Trash}>Delete Item</Button>
                  <Button variant="destructive" size="sm">Small Delete</Button>
                  <Button variant="destructive" disabled>Disabled Delete</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Inputs Section */}
          <TabsContent value="inputs" className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>Input Fields</CardTitle>
                <CardDescription>Text inputs, selects, and form controls</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Text Inputs</h3>
                    <Input 
                      label="Default Input"
                      placeholder="Enter text here..." 
                    />
                    <Input 
                      label="Disabled Input"
                      placeholder="Disabled input" 
                      disabled 
                    />
                    <Input 
                      label="With Icon"
                      icon={Search} 
                      placeholder="Search..." 
                    />
                    <Input 
                      label="With Right Icon"
                      icon={Search} 
                      iconPosition="right"
                      placeholder="Search..." 
                    />
                    <Input 
                      label="With Error"
                      placeholder="Enter email" 
                      error="Please enter a valid email address"
                    />
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Other Form Controls</h3>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Select</label>
                      <select className="w-full rounded-md border border-border bg-card px-3 py-2 text-sm focus:border-ring focus:outline-none">
                        <option value="option1">Option 1</option>
                        <option value="option2">Option 2</option>
                        <option value="option3">Option 3</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Textarea</label>
                      <textarea 
                        className="w-full rounded-md border border-border bg-card px-3 py-2 text-sm focus:border-ring focus:outline-none" 
                        placeholder="Enter multiple lines of text..."
                        rows={3}
                      />
                    </div>
                    <div className="flex items-center space-x-2">
                      <input 
                        type="checkbox" 
                        id="checkbox" 
                        className="h-4 w-4 rounded border-border text-primary focus:ring-ring" 
                      />
                      <label htmlFor="checkbox" className="text-sm font-medium">Checkbox</label>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Added Toggle Group Example */}
            <Card>
              <CardHeader>
                <CardTitle>Toggle Group</CardTitle>
                <CardDescription>Grouped buttons for selecting a single option</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Default Toggle Group</h3>
                    <ToggleGroup type="single" defaultValue="center" aria-label="Text alignment">
                      <ToggleGroupItem value="left" aria-label="Left aligned">
                        Left
                      </ToggleGroupItem>
                      <ToggleGroupItem value="center" aria-label="Center aligned">
                        Center
                      </ToggleGroupItem>
                      <ToggleGroupItem value="right" aria-label="Right aligned">
                        Right
                      </ToggleGroupItem>
                    </ToggleGroup>
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Disabled Toggle Group</h3>
                    <ToggleGroup type="single" defaultValue="center" aria-label="Text alignment" disabled>
                      <ToggleGroupItem value="left" aria-label="Left aligned">
                        Left
                      </ToggleGroupItem>
                      <ToggleGroupItem value="center" aria-label="Center aligned">
                        Center
                      </ToggleGroupItem>
                      <ToggleGroupItem value="right" aria-label="Right aligned">
                        Right
                      </ToggleGroupItem>
                    </ToggleGroup>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Cards Section */}
          <TabsContent value="cards" className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>Cards</CardTitle>
                <CardDescription>Card components for displaying content</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Basic Card</CardTitle>
                      <CardDescription>A simple card with header and content</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm">This is a basic card component that can be used to display content in a contained area.</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle icon={Settings}>Card with Icon</CardTitle>
                      <CardDescription>Includes an icon in the title</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm">This card includes a footer section with action buttons.</p>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                      <Button variant="outline" size="sm">Cancel</Button>
                      <Button size="sm">Save</Button>
                    </CardFooter>
                  </Card>

                  <Card>
                    <CardHeader highlighted>
                      <CardTitle>Featured Card</CardTitle>
                      <CardDescription>With highlighted header</CardDescription>
                    </CardHeader>
                    <CardContent className="pt-4">
                      <p className="text-sm">This card has a highlighted header to make it stand out.</p>
                    </CardContent>
                    <CardFooter highlighted>
                      <p className="text-xs text-amber-400/70">Last updated: 2 days ago</p>
                    </CardFooter>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tables Section */}
          <TabsContent value="tables" className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>Basic Table</CardTitle>
                <CardDescription>Simple table for displaying data</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow> 
                      <TableHead className="font-medium cursor-pointer">Name</TableHead>
                      <TableHead className="font-medium cursor-pointer">Email</TableHead>
                      <TableHead className="font-medium cursor-pointer">Role</TableHead>
                      <TableHead className="font-medium cursor-pointer">Status</TableHead>
                      <TableHead className="font-medium cursor-pointer text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>John Doe</TableCell>
                      <TableCell>john@example.com</TableCell>
                      <TableCell>Admin</TableCell>
                      <TableCell>
                        <StatusBadge status="active">Active</StatusBadge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Jane Smith</TableCell>
                      <TableCell>jane@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="pending">Pending</StatusBadge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Robert Johnson</TableCell>
                      <TableCell>robert@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="inactive">Inactive</StatusBadge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Searchable Table</CardTitle>
                <CardDescription>Table with search functionality</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4 flex items-center gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500 dark:text-gray-300" />
                    <Input
                      type="search"
                      placeholder="Search users..."
                      className="w-full pl-9"
                    />
                  </div>
                  <Button variant="outline" size="sm">Search</Button>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="font-medium cursor-pointer">Name</TableHead>
                      <TableHead className="font-medium cursor-pointer">Email</TableHead>
                      <TableHead className="font-medium cursor-pointer">Role</TableHead>
                      <TableHead className="font-medium cursor-pointer">Status</TableHead>
                      <TableHead className="font-medium cursor-pointer text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>John Doe</TableCell>
                      <TableCell>john@example.com</TableCell>
                      <TableCell>Admin</TableCell>
                      <TableCell>
                        <StatusBadge status="active">Active</StatusBadge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Jane Smith</TableCell>
                      <TableCell>jane@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="pending">Pending</StatusBadge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Robert Johnson</TableCell>
                      <TableCell>robert@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="inactive">Inactive</StatusBadge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Filterable Table</CardTitle>
                <CardDescription>Table with filtering options</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4 flex flex-wrap items-center gap-2">
                  <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500 dark:text-gray-300" />
                    <Input
                      type="search"
                      placeholder="Search users..."
                      className="w-full pl-9"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" className="flex items-center gap-1">
                      <Filter className="h-4 w-4" />
                      <span>Filter</span>
                      <ChevronDown className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm" className="flex items-center gap-1">
                      <span>Status</span>
                      <ChevronDown className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm" className="flex items-center gap-1">
                      <span>Role</span>
                      <ChevronDown className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[40px] font-medium cursor-pointer">
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                          <Check className="h-3 w-3" />
                        </div>
                      </TableHead>
                      <TableHead className="font-medium cursor-pointer">Name</TableHead>
                      <TableHead className="font-medium cursor-pointer">Email</TableHead>
                      <TableHead className="font-medium cursor-pointer">Role</TableHead>
                      <TableHead className="font-medium cursor-pointer">Status</TableHead>
                      <TableHead className="font-medium cursor-pointer">Created</TableHead>
                      <TableHead className="font-medium cursor-pointer">Last Login</TableHead>
                      <TableHead className="font-medium cursor-pointer text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                          <Check className="h-3 w-3" />
                        </div>
                      </TableCell>
                      <TableCell>John Doe</TableCell>
                      <TableCell>john@example.com</TableCell>
                      <TableCell>Admin</TableCell>
                      <TableCell>
                        <StatusBadge status="active">Active</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-12</TableCell>
                      <TableCell>2023-06-01</TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                        </div>
                      </TableCell>
                      <TableCell>Jane Smith</TableCell>
                      <TableCell>jane@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="pending">Pending</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-15</TableCell>
                      <TableCell>2023-05-30</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                          <Check className="h-3 w-3" />
                        </div>
                      </TableCell>
                      <TableCell>Robert Johnson</TableCell>
                      <TableCell>robert@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="inactive">Inactive</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-20</TableCell>
                      <TableCell>2023-05-25</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
                <div className="mt-4 flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    Showing <strong>1-3</strong> of <strong>10</strong> results
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" disabled>Previous</Button>
                    <Button variant="outline" size="sm">Next</Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Compact Table</CardTitle>
                <CardDescription>Smaller, more condensed table for space efficiency</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow className="h-8">
                      <TableHead className="text-xs font-medium cursor-pointer">Name</TableHead>
                      <TableHead className="text-xs font-medium cursor-pointer">Email</TableHead>
                      <TableHead className="text-xs font-medium cursor-pointer">Role</TableHead>
                      <TableHead className="text-xs font-medium cursor-pointer">Status</TableHead>
                      <TableHead className="text-xs font-medium cursor-pointer text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="h-8">
                      <TableCell className="py-1 text-xs">John Doe</TableCell>
                      <TableCell className="py-1 text-xs">john@example.com</TableCell>
                      <TableCell className="py-1 text-xs">Admin</TableCell>
                      <TableCell className="py-1 text-xs">
                        <StatusBadge status="active" className="text-xs py-0 px-2">Active</StatusBadge>
                      </TableCell>
                      <TableCell className="py-1 text-right">
                        <Button variant="ghost" size="xs" icon={Edit} aria-label="Edit" />
                      </TableCell>
                    </TableRow>
                    <TableRow className="h-8">
                      <TableCell className="py-1 text-xs">Jane Smith</TableCell>
                      <TableCell className="py-1 text-xs">jane@example.com</TableCell>
                      <TableCell className="py-1 text-xs">User</TableCell>
                      <TableCell className="py-1 text-xs">
                        <StatusBadge status="pending" className="text-xs py-0 px-2">Pending</StatusBadge>
                      </TableCell>
                      <TableCell className="py-1 text-right">
                        <Button variant="ghost" size="xs" icon={Edit} aria-label="Edit" />
                      </TableCell>
                    </TableRow>
                    <TableRow className="h-8">
                      <TableCell className="py-1 text-xs">Robert Johnson</TableCell>
                      <TableCell className="py-1 text-xs">robert@example.com</TableCell>
                      <TableCell className="py-1 text-xs">User</TableCell>
                      <TableCell className="py-1 text-xs">
                        <StatusBadge status="inactive" className="text-xs py-0 px-2">Inactive</StatusBadge>
                      </TableCell>
                      <TableCell className="py-1 text-right">
                        <Button variant="ghost" size="xs" icon={Edit} aria-label="Edit" />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Skinny Sidebar Table</CardTitle>
                <CardDescription>Compact table optimized for sidebar display with sorting and selection</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="w-full md:w-80 lg:w-96 border border-slate-200 dark:border-slate-800">
                  <SkinnyTable
                    data={[
                      { id: 1, sku: "PRD001", name: "Product One", status: "active" },
                      { id: 2, sku: "PRD002", name: "Product Two", status: "inactive" },
                      { id: 3, sku: "PRD003", name: "Product Three", status: "active" },
                    ]}
                    columns={[
                      { field: "sku", header: "SKU" },
                      { field: "name", header: "Name" },
                      {
                        field: "status",
                        header: "Status",
                        render: (item) => (
                          <StatusBadge
                            status={item.status as "active" | "inactive"}
                            className="text-xs"
                          >
                            {item.status === "active" ? "Active" : "Inactive"}
                          </StatusBadge>
                        ),
                      },
                    ]}
                    selectedItem={2}
                    onItemSelect={(item) => console.log("Selected item:", item)}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Selectable Table</CardTitle>
                <CardDescription>Table with row selection capabilities</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" className="flex items-center gap-1">
                      <span>Bulk Actions</span>
                      <ChevronDown className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm" icon={Trash}>Delete Selected</Button>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500 dark:text-gray-300" />
                      <Input
                        type="search"
                        placeholder="Search..."
                        className="w-[200px] pl-9"
                      />
                    </div>
                  </div>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[40px] font-medium cursor-pointer">
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                          <Check className="h-3 w-3" />
                        </div>
                      </TableHead>
                      <TableHead className="font-medium cursor-pointer">Name</TableHead>
                      <TableHead className="font-medium cursor-pointer">Email</TableHead>
                      <TableHead className="font-medium cursor-pointer">Role</TableHead>
                      <TableHead className="font-medium cursor-pointer">Status</TableHead>
                      <TableHead className="font-medium cursor-pointer">Created</TableHead>
                      <TableHead className="font-medium cursor-pointer">Last Login</TableHead>
                      <TableHead className="font-medium cursor-pointer text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                          <Check className="h-3 w-3" />
                        </div>
                      </TableCell>
                      <TableCell>John Doe</TableCell>
                      <TableCell>john@example.com</TableCell>
                      <TableCell>Admin</TableCell>
                      <TableCell>
                        <StatusBadge status="active">Active</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-12</TableCell>
                      <TableCell>2023-06-01</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                        </div>
                      </TableCell>
                      <TableCell>Jane Smith</TableCell>
                      <TableCell>jane@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="pending">Pending</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-15</TableCell>
                      <TableCell>2023-05-30</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                          <Check className="h-3 w-3" />
                        </div>
                      </TableCell>
                      <TableCell>Robert Johnson</TableCell>
                      <TableCell>robert@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="inactive">Inactive</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-20</TableCell>
                      <TableCell>2023-05-25</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
                <div className="mt-4 flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    <strong>2</strong> items selected
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" disabled>Previous</Button>
                    <Button variant="outline" size="sm">Next</Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Data Grid</CardTitle>
                <CardDescription>Advanced table with multiple features</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500 dark:text-gray-300" />
                      <Input
                        type="search"
                        placeholder="Search..."
                        className="w-[200px] pl-9"
                      />
                    </div>
                    <Button variant="outline" size="sm" className="flex items-center gap-1">
                      <Filter className="h-4 w-4" />
                      <span>Filters</span>
                      <Badge className="ml-1 bg-amber-500">3</Badge>
                    </Button>
                    <Button variant="outline" size="sm" icon={RefreshCw}>Refresh</Button>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" icon={Download}>Export</Button>
                    <Button variant="outline" size="sm" icon={Settings}>Columns</Button>
                    <Button size="sm" icon={Plus}>Add User</Button>
                  </div>
                </div>
                <div className="mb-2 flex items-center gap-2">
                  <div className="flex items-center gap-1 rounded-md bg-amber-500/10 px-2 py-1 text-xs text-amber-500">
                    <span>Status: Active</span>
                    <X className="h-3 w-3 cursor-pointer" />
                  </div>
                  <div className="flex items-center gap-1 rounded-md bg-amber-500/10 px-2 py-1 text-xs text-amber-500">
                    <span>Role: Admin</span>
                    <X className="h-3 w-3 cursor-pointer" />
                  </div>
                  <div className="flex items-center gap-1 rounded-md bg-amber-500/10 px-2 py-1 text-xs text-amber-500">
                    <span>Created: Last 7 days</span>
                    <X className="h-3 w-3 cursor-pointer" />
                  </div>
                  <Button variant="link" size="sm" className="h-auto p-0 text-xs">Clear all</Button>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[40px] font-medium cursor-pointer">
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                          <Check className="h-3 w-3" />
                        </div>
                      </TableHead>
                      <TableHead className="font-medium cursor-pointer">
                        <div className="flex items-center gap-1">
                          <span>Name</span>
                          <ArrowUpDown className="h-4 w-4" />
                        </div>
                      </TableHead>
                      <TableHead className="font-medium cursor-pointer">
                        <div className="flex items-center gap-1">
                          <span>Email</span>
                          <ArrowUpDown className="h-4 w-4" />
                        </div>
                      </TableHead>
                      <TableHead className="font-medium cursor-pointer">
                        <div className="flex items-center gap-1">
                          <span>Role</span>
                          <ArrowUpDown className="h-4 w-4" />
                        </div>
                      </TableHead>
                      <TableHead className="font-medium cursor-pointer">
                        <div className="flex items-center gap-1">
                          <span>Status</span>
                          <ArrowUpDown className="h-4 w-4" />
                        </div>
                      </TableHead>
                      <TableHead className="font-medium cursor-pointer">
                        <div className="flex items-center gap-1">
                          <span>Created</span>
                          <ArrowUpDown className="h-4 w-4" />
                        </div>
                      </TableHead>
                      <TableHead className="font-medium cursor-pointer">
                        <div className="flex items-center gap-1">
                          <span>Last Login</span>
                          <ArrowUpDown className="h-4 w-4" />
                        </div>
                      </TableHead>
                      <TableHead className="font-medium cursor-pointer text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                          <Check className="h-3 w-3" />
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">John Doe</TableCell>
                      <TableCell>john@example.com</TableCell>
                      <TableCell>Admin</TableCell>
                      <TableCell>
                        <StatusBadge status="active">Active</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-12</TableCell>
                      <TableCell>2023-06-01</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">Jane Smith</TableCell>
                      <TableCell>jane@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="pending">Pending</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-15</TableCell>
                      <TableCell>2023-05-30</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                          <Check className="h-3 w-3" />
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">Robert Johnson</TableCell>
                      <TableCell>robert@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="inactive">Inactive</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-20</TableCell>
                      <TableCell>2023-05-25</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">Emily Davis</TableCell>
                      <TableCell>emily@example.com</TableCell>
                      <TableCell>Admin</TableCell>
                      <TableCell>
                        <StatusBadge status="active">Active</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-22</TableCell>
                      <TableCell>2023-06-02</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-border">
                          <Check className="h-3 w-3" />
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">Michael Wilson</TableCell>
                      <TableCell>michael@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="active">Active</StatusBadge>
                      </TableCell>
                      <TableCell>2023-05-25</TableCell>
                      <TableCell>2023-06-03</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
                <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span>Showing</span>
                    <select className="rounded border border-gray-300 px-2 py-1 text-sm">
                      <option>10</option>
                      <option>20</option>
                      <option>50</option>
                      <option>100</option>
                    </select>
                    <span>of <strong>42</strong> items</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button variant="outline" size="sm" disabled>Previous</Button>
                    <Button variant="outline" size="sm" className="bg-amber-500 text-white hover:bg-amber-600">1</Button>
                    <Button variant="outline" size="sm">2</Button>
                    <Button variant="outline" size="sm">3</Button>
                    <Button variant="outline" size="sm">4</Button>
                    <Button variant="outline" size="sm">Next</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Charts Section */}
          <TabsContent value="charts" className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>Charts</CardTitle>
                <CardDescription>Chart components for data visualization with dark mode support</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Line Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle icon={LineChart}>Line Chart</CardTitle>
                      <CardDescription>Display trend data with a line chart</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                      <div className="w-full h-full bg-muted/30 rounded-md p-2">
                        <ResponsiveContainer width="100%" height="100%">
                          <RechartsLineChart data={lineData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" strokeOpacity={0.5} />
                            <XAxis 
                              dataKey="name" 
                              stroke="var(--muted-foreground)" 
                              fontSize={12} 
                              tickLine={false} 
                              axisLine={false} 
                            />
                            <YAxis 
                              stroke="var(--muted-foreground)" 
                              fontSize={12} 
                              tickLine={false} 
                              axisLine={false} 
                              tickFormatter={(value) => `${value}`}
                            />
                            <Tooltip 
                              contentStyle={{ 
                                backgroundColor: 'var(--popover)', 
                                borderColor: 'var(--border)',
                                color: 'var(--popover-foreground)',
                                borderRadius: 'var(--radius)',
                                boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                              }} 
                              cursor={{ fill: 'transparent' }}
                            />
                            <Legend wrapperStyle={{ fontSize: "12px", color: 'var(--muted-foreground)' }} />
                            <Line 
                              type="monotone" 
                              dataKey="value" 
                              stroke="var(--primary)" 
                              strokeWidth={2} 
                              activeDot={{ r: 8, fill: 'var(--primary)' }} 
                              dot={{ stroke: 'var(--primary)', strokeWidth: 1, r: 4, fill: 'var(--background)' }}
                            />
                          </RechartsLineChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Bar Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle icon={BarChart4}>Bar Chart</CardTitle>
                      <CardDescription>Compare data with a bar chart</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                      <div className="w-full h-full bg-muted/30 rounded-md p-2">
                        <ResponsiveContainer width="100%" height="100%">
                          <RechartsBarChart data={barData} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" strokeOpacity={0.5} vertical={false} />
                            <XAxis 
                              dataKey="name" 
                              stroke="var(--muted-foreground)" 
                              fontSize={12} 
                              tickLine={false} 
                              axisLine={false} 
                            />
                            <YAxis 
                              stroke="var(--muted-foreground)" 
                              fontSize={12} 
                              tickLine={false} 
                              axisLine={false} 
                              tickFormatter={(value) => `${value}`}
                              width={30}
                            />
                            <Tooltip 
                              contentStyle={{ 
                                backgroundColor: 'var(--popover)', 
                                borderColor: 'var(--border)',
                                color: 'var(--popover-foreground)',
                                borderRadius: 'var(--radius)',
                                boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                              }} 
                              cursor={{ fill: 'var(--accent)', opacity: 0.3 }}
                            />
                            <Legend wrapperStyle={{ fontSize: "12px", color: 'var(--muted-foreground)' }} />
                            <Bar dataKey="value" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                          </RechartsBarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Pie Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle icon={PieChart}>Pie Chart</CardTitle>
                      <CardDescription>Show proportion with a pie chart</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                      <div className="w-full h-full bg-muted/30 rounded-md p-2 flex items-center justify-center">
                        <ResponsiveContainer width="100%" height="100%">
                          <RechartsPieChart margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                            <Pie
                              data={pieData}
                              cx="50%"
                              cy="50%"
                              labelLine={false}
                              outerRadius={80}
                              fill="var(--primary)"
                              dataKey="value"
                              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                              fontSize={12}
                              stroke="var(--card)"
                              strokeWidth={2}
                            >
                              <Cell fill="var(--primary)" />
                              <Cell fill="var(--accent)" />
                              <Cell fill="var(--secondary)" />
                              <Cell fill="oklch(from var(--primary) l c calc(h + 180))" />
                            </Pie>
                            <Tooltip 
                              contentStyle={{ 
                                backgroundColor: 'var(--popover)', 
                                borderColor: 'var(--border)',
                                color: 'var(--popover-foreground)',
                                borderRadius: 'var(--radius)',
                                boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                              }} 
                            />
                            <Legend 
                              wrapperStyle={{ fontSize: "12px", color: 'var(--muted-foreground)' }} 
                              verticalAlign="bottom" 
                              height={36} 
                            />
                          </RechartsPieChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Area Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Area Chart</CardTitle>
                      <CardDescription>Visualize volume with area chart</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                      <div className="w-full h-full bg-muted/30 rounded-md p-2">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={areaData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" strokeOpacity={0.5} />
                            <XAxis 
                              dataKey="name" 
                              stroke="var(--muted-foreground)" 
                              fontSize={12} 
                              tickLine={false} 
                              axisLine={false} 
                            />
                            <YAxis 
                              stroke="var(--muted-foreground)" 
                              fontSize={12} 
                              tickLine={false} 
                              axisLine={false} 
                              tickFormatter={(value) => `${value}`}
                              width={30}
                            />
                            <Tooltip 
                              contentStyle={{ 
                                backgroundColor: 'var(--popover)', 
                                borderColor: 'var(--border)',
                                color: 'var(--popover-foreground)',
                                borderRadius: 'var(--radius)',
                                boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                              }} 
                              cursor={{ fill: 'transparent' }}
                            />
                            <Area 
                              type="monotone" 
                              dataKey="value" 
                              stroke="var(--primary)" 
                              fill="var(--primary)" 
                              fillOpacity={0.3} 
                              strokeWidth={2}
                            />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Radar Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Radar Chart</CardTitle>
                      <CardDescription>Multi-dimensional data on a radar chart</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                      <div className="w-full h-full bg-muted/30 rounded-md p-2">
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                            <PolarGrid stroke="var(--border)" strokeOpacity={0.5} />
                            <PolarAngleAxis 
                              dataKey="subject" 
                              stroke="var(--muted-foreground)" 
                              fontSize={12} 
                              tickLine={false} 
                            />
                            <PolarRadiusAxis 
                              stroke="var(--muted-foreground)" 
                              fontSize={10} 
                              axisLine={false} 
                              tickLine={false} 
                            />
                            <Radar 
                              name="Student A" 
                              dataKey="A" 
                              stroke="var(--primary)" 
                              fill="var(--primary)" 
                              fillOpacity={0.6} 
                            />
                            <Radar 
                              name="Student B" 
                              dataKey="B" 
                              stroke="var(--accent)" 
                              fill="var(--accent)" 
                              fillOpacity={0.5} 
                            />
                            <Legend wrapperStyle={{ fontSize: "12px", color: 'var(--muted-foreground)' }} />
                            <Tooltip 
                              contentStyle={{ 
                                backgroundColor: 'var(--popover)', 
                                borderColor: 'var(--border)',
                                color: 'var(--popover-foreground)',
                                borderRadius: 'var(--radius)',
                                boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                              }} 
                            />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Scatter Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Scatter Chart</CardTitle>
                      <CardDescription>Display correlation with scatter plots</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                      <div className="w-full h-full bg-muted/30 rounded-md p-2">
                        <ResponsiveContainer width="100%" height="100%">
                          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" strokeOpacity={0.5} />
                            <XAxis 
                              type="number" 
                              dataKey="x" 
                              name="x-axis" 
                              stroke="var(--muted-foreground)" 
                              fontSize={12} 
                              tickLine={false} 
                              axisLine={false}
                            />
                            <YAxis 
                              type="number" 
                              dataKey="y" 
                              name="y-axis" 
                              stroke="var(--muted-foreground)" 
                              fontSize={12} 
                              tickLine={false} 
                              axisLine={false} 
                              width={30}
                            />
                            <Tooltip 
                              contentStyle={{ 
                                backgroundColor: 'var(--popover)', 
                                borderColor: 'var(--border)',
                                color: 'var(--popover-foreground)',
                                borderRadius: 'var(--radius)',
                                boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                              }} 
                              cursor={{ stroke: 'var(--border)', strokeDasharray: '3 3' }} 
                            />
                            <Scatter name="Values" data={scatterData} fill="var(--primary)" />
                          </ScatterChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Filters Section */}
          <TabsContent value="filters" className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>Filters & Search</CardTitle>
                <CardDescription>Components for filtering and searching data</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="flex flex-col md:flex-row gap-4">
                    <Input 
                      icon={Search}
                      placeholder="Search..." 
                      fullWidth
                    />
                    <Button icon={Search}>Search</Button>
                  </div>

                  <Separator className="my-4" />

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="text-sm font-medium mb-1 block">Status</label>
                      <select className="w-full rounded-md border border-amber-800/35 bg-amber-950/25 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none">
                        <option value="">All Statuses</option>
                        <option value="active">Active</option>
                        <option value="pending">Pending</option>
                        <option value="inactive">Inactive</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-1 block">Category</label>
                      <select className="w-full rounded-md border border-amber-800/35 bg-amber-950/25 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none">
                        <option value="">All Categories</option>
                        <option value="category1">Category 1</option>
                        <option value="category2">Category 2</option>
                        <option value="category3">Category 3</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-1 block">Date Range</label>
                      <select className="w-full rounded-md border border-amber-800/35 bg-amber-950/25 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none">
                        <option value="today">Today</option>
                        <option value="yesterday">Yesterday</option>
                        <option value="last7days">Last 7 Days</option>
                        <option value="last30days">Last 30 Days</option>
                        <option value="custom">Custom Range</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex justify-between mt-4">
                    <Button variant="outline">Reset Filters</Button>
                    <Button icon={Filter}>Apply Filters</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Colors Section */}
          <TabsContent value="colors" className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>Theme Colors</CardTitle>
                <CardDescription>Color variables organized by functional categories</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-8">
                  {colorCategories.map((category) => (
                    <div key={category.category} className="space-y-4">
                      <h3 className="text-lg font-medium">{category.category}</h3>
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-x-4 gap-y-6">
                        {category.colors.map((color) => (
                          <ColorSwatch key={color.name} name={color.name} cssVarName={color.variable} />
                        ))}
                      </div>
                      {category.category !== colorCategories[colorCategories.length - 1].category && (
                        <Separator className="my-4" />
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Icons Section */}
          <TabsContent value="icons" className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>Icons</CardTitle>
                <CardDescription>Lucide icons used throughout the application</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-8">
                  <div>
                    <h3 className="text-lg font-medium mb-4">Common Icons</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <User className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">User</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Home className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Home</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Settings className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Settings</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Search className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Search</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <ShoppingCart className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">ShoppingCart</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <FileText className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">FileText</span>
                      </div>
                    </div>
                  </div>

                  <Separator className="my-6" />

                  <div>
                    <h3 className="text-lg font-medium mb-4">Action Icons</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Plus className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Plus</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Edit className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Edit</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Trash className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Trash</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Save className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Save</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Download className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Download</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Upload className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Upload</span>
                      </div>
                    </div>
                  </div>

                  <Separator className="my-6" />

                  <div>
                    <h3 className="text-lg font-medium mb-4">Notification Icons</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Bell className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Bell</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Mail className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Mail</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Calendar className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Calendar</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Phone className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">Phone</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <CreditCard className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">CreditCard</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <HelpCircle className="h-8 w-8 text-primary mb-2" />
                        <span className="text-xs text-center">HelpCircle</span>
                      </div>
                    </div>
                  </div>

                  <Separator className="my-6" />

                  <div>
                    <h3 className="text-lg font-medium mb-4">Status Icons</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Info className="h-8 w-8 text-blue-500 mb-2" />
                        <span className="text-xs text-center">Info</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <AlertTriangle className="h-8 w-8 text-yellow-500 mb-2" />
                        <span className="text-xs text-center">AlertTriangle</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <CheckCircle className="h-8 w-8 text-green-500 mb-2" />
                        <span className="text-xs text-center">CheckCircle</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <XCircle className="h-8 w-8 text-red-500 mb-2" />
                        <span className="text-xs text-center">XCircle</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <Check className="h-8 w-8 text-green-500 mb-2" />
                        <span className="text-xs text-center">Check</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-md">
                        <X className="h-8 w-8 text-red-500 mb-2" />
                        <span className="text-xs text-center">X</span>
                      </div>
                    </div>
                  </div>

                  <Separator className="my-6" />

                  <div>
                    <h3 className="text-lg font-medium mb-4">Usage Examples</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <h4 className="text-md font-medium">In Buttons</h4>
                        <div className="flex flex-wrap gap-2">
                          <Button icon={Plus}>Add Item</Button>
                          <Button variant="secondary" icon={Edit}>Edit</Button>
                          <Button variant="outline" icon={Trash}>Delete</Button>
                          <Button size="icon" icon={Settings} aria-label="Settings" />
                        </div>
                        <div className="bg-card p-4 rounded-md">
                          <pre className="text-xs overflow-x-auto text-muted-foreground">
{`<Button icon={Plus}>Add Item</Button>
<Button variant="secondary" icon={Edit}>Edit</Button>
<Button variant="outline" icon={Trash}>Delete</Button>
<Button size="icon" icon={Settings} aria-label="Settings" />`}
                          </pre>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="text-md font-medium">In Inputs</h4>
                        <div className="space-y-2">
                          <Input icon={Search} placeholder="Search..." />
                          <Input icon={Mail} placeholder="Email address..." />
                          <Input icon={User} placeholder="Username..." />
                        </div>
                        <div className="bg-card p-4 rounded-md">
                          <pre className="text-xs overflow-x-auto text-muted-foreground">
{`<Input icon={Search} placeholder="Search..." />
<Input icon={Mail} placeholder="Email address..." />
<Input icon={User} placeholder="Username..." />`}
                          </pre>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-card p-6 rounded-md">
                    <h3 className="text-lg font-medium mb-4">How to Use Icons</h3>
                    <p className="text-sm mb-4">
                      This project uses Lucide React for icons. Import the icons you need from the lucide-react package:
                    </p>
                    <pre className="text-xs bg-muted p-4 rounded-md overflow-x-auto mb-4">
{`import { Search, User, Settings } from 'lucide-react';`}
                    </pre>
                    <p className="text-sm mb-4">
                      You can use icons directly in your components:
                    </p>
                    <pre className="text-xs bg-muted p-4 rounded-md overflow-x-auto mb-4">
{`<Search className="h-4 w-4 text-primary" />`}
                    </pre>
                    <p className="text-sm">
                      Or use them with our enhanced components that have built-in icon support:
                    </p>
                    <pre className="text-xs bg-muted p-4 rounded-md overflow-x-auto">
{`<Button icon={Plus}>Add Item</Button>
<Input icon={Search} placeholder="Search..." />
<CardTitle icon={Settings}>Card Title</CardTitle>`}
                    </pre>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// Helper component for displaying color swatches using CSS variables
interface ColorSwatchProps {
  name: string;
  cssVarName: string;
}

const ColorSwatch: React.FC<ColorSwatchProps> = ({ name, cssVarName }) => (
  <div className="flex flex-col items-center space-y-1">
    <div 
      className="h-16 w-full rounded-md border border-border shadow-sm"
      style={{ backgroundColor: `var(${cssVarName})` }}
      title={`${name}: var(${cssVarName})`}
    />
    <span className="text-xs text-muted-foreground">{name}</span>
    <span className="text-xs font-mono text-muted-foreground/70">{`var(${cssVarName})`}</span>
  </div>
); 
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
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  StatusBadge,
  Badge
} from '@/components/ui';
import { themeColors } from '@/lib/theme-config';

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
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
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
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
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
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
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
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
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
                      <TableHead className="flex items-center gap-1">
                        <span>Name</span>
                        <ArrowUpDown className="h-4 w-4" />
                      </TableHead>
                      <TableHead className="flex items-center gap-1">
                        <span>Email</span>
                        <ArrowUpDown className="h-4 w-4" />
                      </TableHead>
                      <TableHead className="flex items-center gap-1">
                        <span>Role</span>
                        <ArrowUpDown className="h-4 w-4" />
                      </TableHead>
                      <TableHead className="flex items-center gap-1">
                        <span>Status</span>
                        <ArrowUpDown className="h-4 w-4" />
                      </TableHead>
                      <TableHead className="text-right">Actions</TableHead>
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
                      <TableHead className="text-xs">Name</TableHead>
                      <TableHead className="text-xs">Email</TableHead>
                      <TableHead className="text-xs">Role</TableHead>
                      <TableHead className="text-xs">Status</TableHead>
                      <TableHead className="text-right text-xs">Actions</TableHead>
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
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
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
                      <TableHead className="w-[40px]">
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300">
                          <Check className="h-3 w-3 text-amber-500" />
                        </div>
                      </TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300">
                          <Check className="h-3 w-3 text-amber-500" />
                        </div>
                      </TableCell>
                      <TableCell>John Doe</TableCell>
                      <TableCell>john@example.com</TableCell>
                      <TableCell>Admin</TableCell>
                      <TableCell>
                        <StatusBadge status="active">Active</StatusBadge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300">
                        </div>
                      </TableCell>
                      <TableCell>Jane Smith</TableCell>
                      <TableCell>jane@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="pending">Pending</StatusBadge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300">
                          <Check className="h-3 w-3 text-amber-500" />
                        </div>
                      </TableCell>
                      <TableCell>Robert Johnson</TableCell>
                      <TableCell>robert@example.com</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>
                        <StatusBadge status="inactive">Inactive</StatusBadge>
                      </TableCell>
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
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
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
                      <TableHead className="w-[40px]">
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300">
                        </div>
                      </TableHead>
                      <TableHead className="flex items-center gap-1">
                        <span>Name</span>
                        <ChevronUp className="h-4 w-4 text-amber-500" />
                      </TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead>Last Login</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300">
                          <Check className="h-3 w-3 text-amber-500" />
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
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300">
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
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300">
                          <Check className="h-3 w-3 text-amber-500" />
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
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300">
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
                        <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300">
                          <Check className="h-3 w-3 text-amber-500" />
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
                <CardDescription>Chart components for data visualization</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle icon={BarChart4}>Bar Chart</CardTitle>
                    </CardHeader>
                    <CardContent className="flex items-center justify-center p-6">
                      <div className="h-40 w-40 flex items-center justify-center rounded-full bg-amber-900/25 text-amber-500">
                        <BarChart4 className="h-16 w-16" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle icon={PieChart}>Pie Chart</CardTitle>
                    </CardHeader>
                    <CardContent className="flex items-center justify-center p-6">
                      <div className="h-40 w-40 flex items-center justify-center rounded-full bg-amber-900/25 text-amber-500">
                        <PieChart className="h-16 w-16" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle icon={LineChart}>Line Chart</CardTitle>
                    </CardHeader>
                    <CardContent className="flex items-center justify-center p-6">
                      <div className="h-40 w-40 flex items-center justify-center rounded-full bg-amber-900/25 text-amber-500">
                        <LineChart className="h-16 w-16" />
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
                <CardTitle>Color Palette</CardTitle>
                <CardDescription>Rich warm brown color scheme for the application</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-lg font-medium mb-4">Primary Colors</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-primary mr-4"></div>
                        <div>
                          <p className="font-medium">Primary</p>
                          <p className="text-sm text-muted-foreground">Primary Color</p>
                          <p className="text-xs text-muted-foreground">{themeColors.primary}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-primary/80 mr-4"></div>
                        <div>
                          <p className="font-medium">Primary (80%)</p>
                          <p className="text-sm text-muted-foreground">Primary Hover</p>
                          <p className="text-xs text-muted-foreground">{themeColors.primaryHover}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-primary/60 mr-4"></div>
                        <div>
                          <p className="font-medium">Primary (60%)</p>
                          <p className="text-sm text-muted-foreground">Primary Active</p>
                          <p className="text-xs text-muted-foreground">{themeColors.primaryActive}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-ring mr-4"></div>
                        <div>
                          <p className="font-medium">Ring</p>
                          <p className="text-sm text-muted-foreground">Focus Ring</p>
                          <p className="text-xs text-muted-foreground">{themeColors.ring}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-4">Background Colors</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-background mr-4 border border-border"></div>
                        <div>
                          <p className="font-medium">Background</p>
                          <p className="text-sm text-muted-foreground">Page Background</p>
                          <p className="text-xs text-muted-foreground">{themeColors.background}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-card mr-4 border border-border"></div>
                        <div>
                          <p className="font-medium">Card</p>
                          <p className="text-sm text-muted-foreground">Card Background</p>
                          <p className="text-xs text-muted-foreground">{themeColors.card}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-muted mr-4 border border-border"></div>
                        <div>
                          <p className="font-medium">Muted</p>
                          <p className="text-sm text-muted-foreground">Muted Background</p>
                          <p className="text-xs text-muted-foreground">{themeColors.muted}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-4">Text Colors</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-card mr-4 border border-border flex items-center justify-center">
                          <span className="text-foreground">Aa</span>
                        </div>
                        <div>
                          <p className="font-medium">Foreground</p>
                          <p className="text-sm text-muted-foreground">Primary Text</p>
                          <p className="text-xs text-muted-foreground">{themeColors.foreground}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-card mr-4 border border-border flex items-center justify-center">
                          <span className="text-primary">Aa</span>
                        </div>
                        <div>
                          <p className="font-medium">Primary</p>
                          <p className="text-sm text-muted-foreground">Accent Text</p>
                          <p className="text-xs text-muted-foreground">{themeColors.primary}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-card mr-4 border border-border flex items-center justify-center">
                          <span className="text-muted-foreground">Aa</span>
                        </div>
                        <div>
                          <p className="font-medium">Muted</p>
                          <p className="text-sm text-muted-foreground">Muted Text</p>
                          <p className="text-xs text-muted-foreground">{themeColors.mutedForeground}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-4">Status Colors</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-transparent mr-4 border-2 border-border"></div>
                        <div>
                          <p className="font-medium">Border</p>
                          <p className="text-sm text-muted-foreground">Border Color</p>
                          <p className="text-xs text-muted-foreground">{themeColors.border}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <StatusBadge status="active" className="mr-4 py-2 px-4">Active</StatusBadge>
                        <div>
                          <p className="font-medium">Green Status</p>
                          <p className="text-sm text-muted-foreground">Active state</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <StatusBadge status="pending" className="mr-4 py-2 px-4">Pending</StatusBadge>
                        <div>
                          <p className="font-medium">Yellow Status</p>
                          <p className="text-sm text-muted-foreground">Pending state</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <StatusBadge status="inactive" className="mr-4 py-2 px-4">Inactive</StatusBadge>
                        <div>
                          <p className="font-medium">Gray Status</p>
                          <p className="text-sm text-muted-foreground">Inactive state</p>
                        </div>
                      </div>
                    </div>
                  </div>
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
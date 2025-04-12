'use client';

import React, { useState } from 'react'; // Import React
import { useForm } from 'react-hook-form'; // Import useForm from react-hook-form
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
  Calendar as CalendarIcon, // Renamed to avoid conflict
  Mail,
  Phone,
  CreditCard,
  HelpCircle,
  Info,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Minus
} from 'lucide-react';

// Import all components from the UI library index
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Input,
  Label,
  RadioGroup, RadioGroupItem,
  Textarea,
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
  Form, FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage,
  Checkbox,
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell, TableCaption,
  Avatar, AvatarImage, AvatarFallback,
  Badge,
  Calendar, // This is the Calendar component
  Separator,
  Alert, AlertDescription, AlertTitle,
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
  Toast, ToastProvider, ToastViewport, ToastTitle, ToastDescription, ToastClose, ToastAction, Toaster,
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger, DialogClose,
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger, DropdownMenuCheckboxItem, DropdownMenuRadioGroup, DropdownMenuRadioItem, DropdownMenuGroup, DropdownMenuPortal, DropdownMenuShortcut, DropdownMenuSub, DropdownMenuSubContent, DropdownMenuSubTrigger,
  Popover, PopoverContent, PopoverTrigger,
  Sheet, SheetClose, SheetContent, SheetDescription, SheetFooter, SheetHeader, SheetTitle, SheetTrigger,
  Tooltip, TooltipContent, TooltipProvider, TooltipTrigger,
  Progress,
  Skeleton,
  Spinner, // Assuming this is the intended Spinner
  LoadingSpinner, // Assuming this is the intended LoadingSpinner
  Slider,
  Switch,
  Tabs, TabsContent, TabsList, TabsTrigger,
  Toggle,
  ToggleGroup, ToggleGroupItem,
  ScrollArea, ScrollBar,
  Container,
  StatusBadge, // Exported from Table component
  themeColors, // Exported from theme config
} from '@/components/ui';

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
  Tooltip as RechartsTooltip, // Rename to avoid conflict
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

import { SkinnyTable } from "@/components/ui/skinny-table"; // Keep this if SkinnyTable is separate

// Import newly added Resizable components
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";

// Sample data for charts (keep existing)
// ... existing chart data ...
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

// Define the semantic colors based on CSS variables in globals.css (keep existing)
// ... existing colorCategories and semanticColors ...
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

const semanticColors = colorCategories.flatMap(category => category.colors);
const statusColors = colorCategories.find(c => c.category === "Status Colors")?.colors || [];


// Define the tabs structure
const componentTabs = [
  { value: 'buttons', label: 'Buttons', components: ['Button'] },
  { value: 'inputs', label: 'Form Controls', components: ['Input', 'Label', 'RadioGroup', 'Textarea', 'Select', 'Form', 'Checkbox', 'Switch', 'Slider', 'Toggle', 'ToggleGroup'] },
  { value: 'dataDisplay', label: 'Data Display', components: ['Table', 'Avatar', 'Badge', 'Calendar', 'Separator', 'StatusBadge', 'SkinnyTable'] },
  { value: 'feedback', label: 'Feedback', components: ['Alert', 'AlertDialog', 'Toast', 'Progress', 'Skeleton', 'Spinner', 'LoadingSpinner'] },
  { value: 'overlays', label: 'Overlays', components: ['Dialog', 'DropdownMenu', 'Popover', 'Sheet', 'Tooltip'] },
  { value: 'layout', label: 'Layout', components: ['Card', 'Tabs', 'ScrollArea', 'Container', 'Resizable'] },
  { value: 'charts', label: 'Charts', components: ['RechartsLineChart', 'RechartsBarChart', 'RechartsPieChart', 'AreaChart', 'RadarChart', 'ScatterChart'] },
  { value: 'icons', label: 'Icons', components: ['Lucide Icons'] },
  { value: 'colors', label: 'Colors', components: ['Semantic Colors', 'Status Colors'] },
];

// Import useToast from the correct location
import { useToast } from '@/hooks/use-toast';

export default function UIComponentsPage() {
  const [activeTab, setActiveTab] = useState(componentTabs[0].value);
  const [date, setDate] = useState<Date | undefined>(new Date());
  const { toast } = useToast();
  // Dummy form setup for Form component example
  const form = useForm();

  return (
    // Use the Container component for consistent padding
    <Container className="py-12"> 
      <ToastProvider>
        <div className="max-w-7xl mx-auto"> {/* Increased max-width for more space */}
        <h1 className="text-3xl font-bold mb-2 text-primary">UI Components / Style Guide</h1>
          <p className="text-muted-foreground mb-8">A comprehensive collection of UI components for the pyERP system</p>

          {/* Updated Tabs structure */}
          <Tabs defaultValue={activeTab} className="w-full" onValueChange={setActiveTab}>
            {/* Use ScrollArea for TabsList if too many tabs */}
            <ScrollArea className="w-full whitespace-nowrap rounded-md mb-8"> {/* Removed border */}
              <TabsList className="grid w-full grid-cols-9 p-1"> {/* Use grid for equal spacing */} 
                {componentTabs.map(tab => (
                  <TabsTrigger key={tab.value} value={tab.value} className="text-sm px-3 py-1.5"> {/* Adjusted padding */}
                    {tab.label}
                  </TabsTrigger>
                ))}
              </TabsList> {/* Fixed closing tag placement */}
              <ScrollBar orientation="horizontal" />
            </ScrollArea>

          {/* Buttons Section */}
          <TabsContent value="buttons" className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>Buttons</CardTitle>
                  <CardDescription>Variations of the Button component</CardDescription>
              </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium mb-3">Variants</h3>
                    <div className="flex flex-wrap gap-3">
                      <Button>Primary (Default)</Button>
                      <Button variant="secondary">Secondary</Button>
                      <Button variant="outline">Outline</Button>
                      <Button variant="ghost">Ghost</Button>
                      <Button variant="link">Link</Button>
                      <Button variant="destructive">Destructive</Button>
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <h3 className="text-lg font-medium mb-3">Sizes</h3>
                    <div className="flex flex-wrap items-center gap-3">
                      <Button size="lg">Large</Button>
                      <Button size="default">Default</Button>
                      <Button size="sm">Small</Button>
                      <Button size="icon" aria-label="Icon Button"><Settings className="h-4 w-4" /></Button>
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <h3 className="text-lg font-medium mb-3">With Icons</h3>
                    <div className="flex flex-wrap gap-3">
                      <Button icon={Plus}>Add Item</Button>
                      <Button variant="secondary" icon={Edit}>Edit Record</Button>
                      <Button variant="destructive" icon={Trash}>Delete</Button>
                      <Button icon={Save} iconPosition="right">Save Changes</Button>
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <h3 className="text-lg font-medium mb-3">States</h3>
                    <div className="flex flex-wrap gap-3">
                      <Button disabled>Disabled</Button>
                      <Button loading>Loading...</Button>
                      <Button variant="secondary" loading>Processing...</Button>
                </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Form Controls Section */}
            <TabsContent value="inputs" className="space-y-8">
              <Card>
                <CardHeader>
                  <CardTitle>Input & Label</CardTitle>
                  <CardDescription>Basic text input fields with labels</CardDescription>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="input-default">Default Input</Label>
                    <Input id="input-default" placeholder="Enter text..." />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="input-icon-left">With Left Icon</Label>
                    <Input id="input-icon-left" icon={Search} placeholder="Search..." />
                </div>
                  <div className="space-y-2">
                    <Label htmlFor="input-icon-right">With Right Icon</Label>
                    <Input id="input-icon-right" icon={Mail} iconPosition="right" placeholder="Enter email..." />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="input-disabled">Disabled Input</Label>
                    <Input id="input-disabled" placeholder="Cannot type" disabled />
                  </div>
                  {/* Input with error is handled by Form component */}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Checkbox</CardTitle>
                  <CardDescription>Standard checkbox for boolean selections</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-6 items-center">
                   <div className="flex items-center space-x-2">
                      <Checkbox id="checkbox-basic" />
                      <Label htmlFor="checkbox-basic">Accept terms</Label>
                  </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox id="checkbox-disabled" disabled />
                      <Label htmlFor="checkbox-disabled" className="text-muted-foreground">Disabled checkbox</Label>
                    </div>
                     <div className="flex items-center space-x-2">
                      <Checkbox id="checkbox-checked-disabled" checked disabled />
                      <Label htmlFor="checkbox-checked-disabled" className="text-muted-foreground">Checked & Disabled</Label>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                  <CardTitle>Radio Group</CardTitle>
                  <CardDescription>Select one option from a set</CardDescription>
              </CardHeader>
              <CardContent>
                  <RadioGroup defaultValue="option-one">
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="option-one" id="r1" />
                      <Label htmlFor="r1">Option One</Label>
                </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="option-two" id="r2" />
                      <Label htmlFor="r2">Option Two</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="option-three" id="r3" disabled />
                      <Label htmlFor="r3" className="text-muted-foreground">Option Three (Disabled)</Label>
                    </div>
                  </RadioGroup>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                  <CardTitle>Select</CardTitle>
                  <CardDescription>Dropdown selection component</CardDescription>
              </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label>Default Select</Label>
                      <Select>
                        <SelectTrigger className="w-[180px]">
                          <SelectValue placeholder="Select a fruit" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="apple">Apple</SelectItem>
                          <SelectItem value="banana">Banana</SelectItem>
                          <SelectItem value="blueberry">Blueberry</SelectItem>
                          <SelectItem value="grapes">Grapes</SelectItem>
                          <SelectItem value="pineapple">Pineapple</SelectItem>
                        </SelectContent>
                      </Select>
                  </div>
                    <div className="space-y-2">
                      <Label>Disabled Select</Label>
                      <Select disabled>
                        <SelectTrigger className="w-[180px]">
                          <SelectValue placeholder="Cannot Select" />
                        </SelectTrigger>
                      </Select>
                    </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Textarea</CardTitle>
                  <CardDescription>Multi-line text input</CardDescription>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                    <Label htmlFor="textarea-default">Default Textarea</Label>
                    <Textarea id="textarea-default" placeholder="Type your message here." />
                    </div>
                    <div className="space-y-2">
                    <Label htmlFor="textarea-disabled">Disabled Textarea</Label>
                    <Textarea id="textarea-disabled" placeholder="Cannot type" disabled />
                    </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Switch</CardTitle>
                  <CardDescription>On/off toggle switch</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-6 items-center">
                    <div className="flex items-center space-x-2">
                        <Switch id="switch-basic" />
                        <Label htmlFor="switch-basic">Basic Switch</Label>
                    </div>
                     <div className="flex items-center space-x-2">
                        <Switch id="switch-disabled" disabled />
                        <Label htmlFor="switch-disabled" className="text-muted-foreground">Disabled Switch</Label>
                  </div>
                    <div className="flex items-center space-x-2">
                        <Switch id="switch-checked-disabled" checked disabled />
                        <Label htmlFor="switch-checked-disabled" className="text-muted-foreground">Checked & Disabled</Label>
                </div>
              </CardContent>
            </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Slider</CardTitle>
                  <CardDescription>Range selection slider</CardDescription>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
                    <div>
                        <Label>Default Slider</Label>
                        <Slider defaultValue={[50]} max={100} step={1} className="mt-2"/>
                    </div>
                    <div>
                        <Label>Disabled Slider</Label>
                        <Slider defaultValue={[25]} max={100} step={1} disabled className="mt-2"/>
                    </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Toggle</CardTitle>
                  <CardDescription>Single on/off button toggle</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-4">
                    <Toggle aria-label="Toggle bold">
                        <Bold className="h-4 w-4" /> {/* Ensure Bold is imported from lucide-react */}
                    </Toggle>
                     <Toggle aria-label="Toggle italic" disabled>
                        <Italic className="h-4 w-4" /> {/* Ensure Italic is imported */}
                    </Toggle>
                    <Toggle size="sm" aria-label="Toggle underline">
                        <Underline className="h-4 w-4" /> {/* Ensure Underline is imported */}
                    </Toggle>
                </CardContent>
              </Card>

            <Card>
              <CardHeader>
                <CardTitle>Toggle Group</CardTitle>
                  <CardDescription>Grouped toggles for multiple selections or single exclusive selection</CardDescription>
              </CardHeader>
                <CardContent className="space-y-4">
                   <div>
                    <Label>Single Selection (like Radio)</Label>
                    <ToggleGroup type="single" defaultValue="center" aria-label="Text alignment" className="mt-2">
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
                   <div>
                    <Label>Multiple Selection</Label>
                    <ToggleGroup type="multiple" aria-label="Font styles" className="mt-2">
                       <ToggleGroupItem value="bold" aria-label="Toggle bold">
                            <Bold className="h-4 w-4" />
                      </ToggleGroupItem>
                        <ToggleGroupItem value="italic" aria-label="Toggle italic">
                            <Italic className="h-4 w-4" />
                      </ToggleGroupItem>
                        <ToggleGroupItem value="underline" aria-label="Toggle underline">
                            <Underline className="h-4 w-4" />
                      </ToggleGroupItem>
                    </ToggleGroup>
                  </div>
                   <div>
                    <Label>Disabled Group</Label>
                    <ToggleGroup type="single" defaultValue="center" aria-label="Disabled alignment" disabled className="mt-2">
                      <ToggleGroupItem value="left">Left</ToggleGroupItem>
                      <ToggleGroupItem value="center">Center</ToggleGroupItem>
                      <ToggleGroupItem value="right">Right</ToggleGroupItem>
                    </ToggleGroup>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                  <CardTitle>Form</CardTitle>
                  <CardDescription>Component for building forms with validation (using react-hook-form)</CardDescription>
              </CardHeader>
              <CardContent>
                  {/* Basic Form Example */}
                  {/* You would typically define a schema (e.g., with Zod) and handle submission */}
                  <Form {...form}>
                    <form onSubmit={form.handleSubmit(() => console.log('Form submitted'))} className="space-y-4">
                      <FormField
                        control={form.control}
                        name="username"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Username</FormLabel>
                            <FormControl>
                              <Input placeholder="johndoe" {...field} />
                            </FormControl>
                            <FormDescription>
                              This is your public display name.
                            </FormDescription>
                            <FormMessage /> {/* Displays validation errors */}
                          </FormItem>
                        )}
                      />
                      <Button type="submit">Submit</Button>
                    </form>
                  </Form>
              </CardContent>
            </Card>
          </TabsContent>

             {/* Data Display Section */}
            <TabsContent value="dataDisplay" className="space-y-8">
            <Card>
              <CardHeader>
                  <CardTitle>Table</CardTitle>
                  <CardDescription>Standard table for structured data</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                    <TableCaption>A list of recent invoices.</TableCaption>
                  <TableHeader>
                    <TableRow> 
                        <TableHead className="w-[100px]">Invoice</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Method</TableHead>
                        <TableHead className="text-right">Amount</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                        <TableCell className="font-medium">INV001</TableCell>
                        <TableCell><StatusBadge status="success">Paid</StatusBadge></TableCell>
                        <TableCell>Credit Card</TableCell>
                        <TableCell className="text-right">$250.00</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell className="font-medium">INV002</TableCell>
                        <TableCell><StatusBadge status="pending">Pending</StatusBadge></TableCell>
                        <TableCell>PayPal</TableCell>
                        <TableCell className="text-right">$150.00</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell className="font-medium">INV003</TableCell>
                        <TableCell><StatusBadge status="error">Failed</StatusBadge></TableCell>
                        <TableCell>Bank Transfer</TableCell>
                        <TableCell className="text-right">$350.00</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

              {/* Add SkinnyTable example if it's used */}
              {typeof SkinnyTable !== 'undefined' && (
            <Card>
              <CardHeader>
                    <CardTitle>Skinny Table</CardTitle>
                    <CardDescription>A compact table variant (if available)</CardDescription>
              </CardHeader>
              <CardContent>
                    {/* Replace with actual SkinnyTable implementation if needed */}
                    <p className="text-muted-foreground">Example for SkinnyTable goes here.</p>
                    {/* <SkinnyTable data={...} columns={...} /> */}
              </CardContent>
            </Card>
              )}

            <Card>
              <CardHeader>
                  <CardTitle>Avatar</CardTitle>
                  <CardDescription>Displays user avatars or placeholders</CardDescription>
              </CardHeader>
                <CardContent className="flex flex-wrap gap-4 items-center">
                    <Avatar>
                      <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
                      <AvatarFallback>CN</AvatarFallback>
                    </Avatar>
                    <Avatar>
                      <AvatarFallback>JD</AvatarFallback> {/* Fallback when no image */}
                    </Avatar>
                    <Avatar className="h-16 w-16"> {/* Custom size */}
                       <AvatarImage src="https://github.com/vercel.png" alt="@vercel" />
                       <AvatarFallback>VC</AvatarFallback>
                    </Avatar>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                  <CardTitle>Badge</CardTitle>
                  <CardDescription>Informational badges</CardDescription>
              </CardHeader>
                <CardContent className="flex flex-wrap gap-3">
                    <Badge>Default</Badge>
                    <Badge variant="secondary">Secondary</Badge>
                    <Badge variant="outline">Outline</Badge>
                    <Badge variant="destructive">Destructive</Badge>
                     {/* StatusBadge is also a type of badge */}
                    <StatusBadge status="success">Success</StatusBadge>
                    <StatusBadge status="warning">Warning</StatusBadge>
                    <StatusBadge status="error">Error</StatusBadge>
                    <StatusBadge status="pending">Pending</StatusBadge>
                    <StatusBadge status="info">Info</StatusBadge>
                    <StatusBadge status="inactive">Inactive</StatusBadge>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                  <CardTitle>Calendar</CardTitle>
                  <CardDescription>Date selection calendar</CardDescription>
              </CardHeader>
                <CardContent className="flex justify-center">
                  <Calendar
                    mode="single"
                    selected={date}
                    onSelect={setDate}
                    className="rounded-md border"
                  />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                  <CardTitle>Separator</CardTitle>
                  <CardDescription>Visual separator line</CardDescription>
              </CardHeader>
              <CardContent>
                    <div>
                        <p>Content above the separator.</p>
                        <Separator className="my-4" />
                        <p>Content below the separator.</p>
                  </div>
                     <div className="flex h-10 items-center space-x-4 text-sm mt-6">
                        <div>Blog</div>
                        <Separator orientation="vertical" />
                        <div>Docs</div>
                        <Separator orientation="vertical" />
                        <div>Source</div>
                </div>
              </CardContent>
            </Card>
            </TabsContent>

            {/* Feedback Section */}
            <TabsContent value="feedback" className="space-y-8">
            <Card>
              <CardHeader>
                  <CardTitle>Toast</CardTitle>
                  <CardDescription>Toast notifications system</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Click the buttons below to see toast notifications in action:</p>
                  <div className="flex flex-wrap gap-3">
                    <Button
                      onClick={() => {
                        toast({
                          title: "Default Toast",
                          description: "This is a default toast notification",
                        })
                      }}
                    >
                      Show Toast
                    </Button>
                    <Button
                      variant="destructive"
                      onClick={() => {
                        toast({
                          variant: "destructive",
                          title: "Error Toast",
                          description: "Something went wrong!",
                        })
                      }}
                    >
                      Show Error Toast
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {
                        toast({
                          title: "Toast with Action",
                          description: "This toast has an action button",
                          action: (
                            <ToastAction altText="Try again" onClick={() => alert("Action clicked!")}>
                              Try again
                            </ToastAction>
                          ),
                        })
                      }}
                    >
                      Toast with Action
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                  <CardTitle>Alert</CardTitle>
                  <CardDescription>Displays important messages</CardDescription>
              </CardHeader>
                <CardContent className="space-y-4">
                  <Alert>
                    <Info className="h-4 w-4" />
                    <AlertTitle>Heads up!</AlertTitle>
                    <AlertDescription>
                      You can add components to your app using the cli.
                    </AlertDescription>
                  </Alert>
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>
                      Your session has expired. Please log in again.
                    </AlertDescription>
                  </Alert>
                  <Alert>
                     <CheckCircle className="h-4 w-4" />
                    <AlertTitle>Success</AlertTitle>
                    <AlertDescription>
                      Your changes have been saved successfully.
                    </AlertDescription>
                  </Alert>
                   <Alert>
                     <AlertTriangle className="h-4 w-4" />
                    <AlertTitle>Warning</AlertTitle>
                    <AlertDescription>
                      Please backup your data before proceeding.
                    </AlertDescription>
                  </Alert>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                  <CardTitle>Alert Dialog</CardTitle>
                  <CardDescription>Modal dialog for critical confirmations</CardDescription>
              </CardHeader>
              <CardContent>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive">Delete Account</Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This action cannot be undone. This will permanently delete your
                          account and remove your data from our servers.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction>Continue</AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </CardContent>
              </Card>

                  <Card>
                    <CardHeader>
                  <CardTitle>Progress</CardTitle>
                  <CardDescription>Indicates the progress of an operation</CardDescription>
                    </CardHeader>
                <CardContent className="pt-4">
                   <Label>Loading...</Label>
                   <Progress value={33} className="mt-2"/>
                   <Label className="mt-4 block">Upload Complete</Label>
                   <Progress value={100} className="mt-2" />
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                  <CardTitle>Skeleton</CardTitle>
                  <CardDescription>Placeholder for loading content</CardDescription>
                    </CardHeader>
                <CardContent className="space-y-4">
                   <div className="flex items-center space-x-4">
                      <Skeleton className="h-12 w-12 rounded-full" />
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-[250px]" />
                        <Skeleton className="h-4 w-[200px]" />
                      </div>
                    </div>
                    <Skeleton className="h-32 w-full rounded-md" />
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                  <CardTitle>Spinners</CardTitle>
                  <CardDescription>Indicates loading or processing state</CardDescription>
                    </CardHeader>
                <CardContent className="flex flex-wrap gap-6 items-center">
                   {typeof Spinner !== 'undefined' && (
                     <div className="flex flex-col items-center gap-2">
                        <Label>Spinner</Label>
                        <Spinner />
                      </div>
                   )}
                   {typeof LoadingSpinner !== 'undefined' && (
                      <div className="flex flex-col items-center gap-2">
                        <Label>LoadingSpinner</Label>
                        <LoadingSpinner />
                      </div>
                   )}
                   {/* Show loading state on button as well */}
                   <Button loading>Button Loading</Button>
                    </CardContent>
                  </Card>

            </TabsContent>

            {/* Overlays Section */}
            <TabsContent value="overlays" className="space-y-8">
                  <Card>
                    <CardHeader>
                  <CardTitle>Dialog</CardTitle>
                  <CardDescription>Modal window for focused tasks or information</CardDescription>
                    </CardHeader>
                <CardContent>
                   <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline">Edit Profile</Button>
                      </DialogTrigger>
                      <DialogContent className="sm:max-w-[425px]">
                        <DialogHeader>
                          <DialogTitle>Edit profile</DialogTitle>
                          <DialogDescription>
                            Make changes to your profile here. Click save when you're done.
                          </DialogDescription>
                        </DialogHeader>
                        <div className="grid gap-4 py-4">
                          <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="name" className="text-right">
                              Name
                            </Label>
                            <Input id="name" value="Pedro Duarte" className="col-span-3" />
                      </div>
                          <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="username" className="text-right">
                              Username
                            </Label>
                            <Input id="username" value="@peduarte" className="col-span-3" />
                          </div>
                        </div>
                        <DialogFooter>
                          <DialogClose asChild>
                            <Button type="button" variant="secondary">Close</Button>
                          </DialogClose>
                          <Button type="submit">Save changes</Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                  <CardTitle>Dropdown Menu</CardTitle>
                  <CardDescription>Contextual menu triggered by a button</CardDescription>
                    </CardHeader>
                <CardContent>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline">Open Menu</Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56">
                      <DropdownMenuLabel>My Account</DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuGroup>
                        <DropdownMenuItem>
                          <User className="mr-2 h-4 w-4" />
                          <span>Profile</span>
                          <DropdownMenuShortcut>⇧⌘P</DropdownMenuShortcut>
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <CreditCard className="mr-2 h-4 w-4" />
                          <span>Billing</span>
                          <DropdownMenuShortcut>⌘B</DropdownMenuShortcut>
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Settings className="mr-2 h-4 w-4" />
                          <span>Settings</span>
                          <DropdownMenuShortcut>⌘S</DropdownMenuShortcut>
                        </DropdownMenuItem>
                      </DropdownMenuGroup>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem disabled>
                        <Mail className="mr-2 h-4 w-4" />
                        <span>Email (Disabled)</span>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem>
                        <LogOut className="mr-2 h-4 w-4" /> {/* Ensure LogOut imported */}
                        <span>Log out</span>
                        <DropdownMenuShortcut>⇧⌘Q</DropdownMenuShortcut>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                    </CardContent>
                  </Card>

            <Card>
              <CardHeader>
                  <CardTitle>Popover</CardTitle>
                  <CardDescription>Floating content panel triggered by an element</CardDescription>
              </CardHeader>
              <CardContent>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline">Open popover</Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-80">
                      <div className="grid gap-4">
                        <div className="space-y-2">
                          <h4 className="font-medium leading-none">Dimensions</h4>
                          <p className="text-sm text-muted-foreground">
                            Set the dimensions for the layer.
                          </p>
                  </div>
                        <div className="grid gap-2">
                          <div className="grid grid-cols-3 items-center gap-4">
                            <Label htmlFor="width">Width</Label>
                            <Input id="width" defaultValue="100%" className="col-span-2 h-8" />
                    </div>
                          {/* Add more inputs as needed */}
                    </div>
                    </div>
                    </PopoverContent>
                  </Popover>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Sheet</CardTitle>
                  <CardDescription>Side panel that slides in</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-3">
                    <Sheet>
                      <SheetTrigger asChild><Button variant="outline">Open Right Sheet</Button></SheetTrigger>
                      <SheetContent> {/* Defaults to right side */}
                        <SheetHeader>
                          <SheetTitle>Edit profile</SheetTitle>
                          <SheetDescription>
                            Make changes to your profile here. Click save when you're done.
                          </SheetDescription>
                        </SheetHeader>
                        {/* Add content here */}
                         <SheetFooter>
                            <SheetClose asChild>
                                <Button type="submit">Save changes</Button>
                            </SheetClose>
                        </SheetFooter>
                      </SheetContent>
                    </Sheet>
                     <Sheet>
                      <SheetTrigger asChild><Button variant="outline">Open Left Sheet</Button></SheetTrigger>
                      <SheetContent side="left">
                        <SheetHeader>
                          <SheetTitle>Navigation</SheetTitle>
                        </SheetHeader>
                        {/* Add navigation links here */}
                      </SheetContent>
                    </Sheet>
                    {/* Add triggers for top/bottom if needed */}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                  <CardTitle>Tooltip</CardTitle>
                  <CardDescription>Small informational pop-up on hover</CardDescription>
              </CardHeader>
              <CardContent>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="outline" size="icon" aria-label="Add to library">
                          <Plus className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Add to library</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
              </CardContent>
            </Card>
          </TabsContent>

            {/* Layout Section */}
            <TabsContent value="layout" className="space-y-8">
              {/* Card example is already shown in other sections, but we can add a note */}
            <Card>
              <CardHeader>
                  <CardTitle>Card</CardTitle>
                  <CardDescription>Basic container for content sections (Examples shown throughout)</CardDescription>
              </CardHeader>
              <CardContent>
                   <p className="text-muted-foreground">See examples in Buttons, Inputs, etc.</p>
                   <Card className="mt-4 w-fit"> {/* Nested card */}
                       <CardHeader>
                           <CardTitle>Nested Card</CardTitle>
                       </CardHeader>
                       <CardContent>Content inside nested card.</CardContent>
                   </Card>
                </CardContent>
              </Card>

               {/* Tabs example is the main structure of this page */}
               <Card>
                <CardHeader>
                  <CardTitle>Tabs</CardTitle>
                  <CardDescription>Used to organize content into sections (This page uses Tabs)</CardDescription>
                </CardHeader>
                <CardContent>
                    <Tabs defaultValue="account" className="w-[400px]">
                      <TabsList>
                        <TabsTrigger value="account">Account</TabsTrigger>
                        <TabsTrigger value="password">Password</TabsTrigger>
                      </TabsList>
                      <TabsContent value="account">Make changes to your account here.</TabsContent>
                      <TabsContent value="password">Change your password here.</TabsContent>
                    </Tabs>
                </CardContent>
              </Card>

               <Card>
                <CardHeader>
                  <CardTitle>Scroll Area</CardTitle>
                  <CardDescription>Provides scrollbars for content overflow</CardDescription>
                </CardHeader>
                <CardContent>
                    <ScrollArea className="h-32 w-48 rounded-md border p-4">
                        Jokester began sneaking into the castle in the middle of the night
                        and leaving jokes all over the place: on the king's throne, in
                        his soup, even in the royal toilet. The king was furious, but
                        he couldn't seem to stop Jokester.
                    </ScrollArea>
                     {/* Example with horizontal scroll */}
                     <ScrollArea className="w-96 whitespace-nowrap rounded-md border mt-4">
                      <div className="flex w-max space-x-4 p-4">
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
                          <figure key={i} className="shrink-0">
                            <div className="overflow-hidden rounded-md">
                              <div className="bg-muted h-32 w-32 flex items-center justify-center">Item {i}</div>
                      </div>
                            <figcaption className="pt-2 text-xs text-muted-foreground">
                              Image {i}
                            </figcaption>
                          </figure>
                        ))}
                      </div>
                      <ScrollBar orientation="horizontal" />
                    </ScrollArea>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Container</CardTitle>
                  <CardDescription>Applies consistent horizontal padding (used for this page)</CardDescription>
                </CardHeader>
                <CardContent>
                  <Container className="border border-dashed p-4">
                    <p>This content is inside a Container component.</p>
                  </Container>
                </CardContent>
              </Card>

              {/* ADDED: Resizable Panels Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Resizable Panels</CardTitle>
                  <CardDescription>Allows users to resize panels horizontally or vertically.</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">Horizontal Example:</p>
                  <ResizablePanelGroup
                    direction="horizontal"
                    className="max-w-md rounded-lg border h-48 mb-6" // Example sizing and margin
                  >
                    <ResizablePanel defaultSize={50}>
                      <div className="flex h-full items-center justify-center p-6">
                        <span className="font-semibold">Left Panel</span>
                      </div>
                    </ResizablePanel>
                    <ResizableHandle withHandle />
                    <ResizablePanel defaultSize={50}>
                      <div className="flex h-full items-center justify-center p-6">
                        <span className="font-semibold">Right Panel</span>
                      </div>
                    </ResizablePanel>
                  </ResizablePanelGroup>

                  <p className="text-sm text-muted-foreground mb-4">Vertical Example:</p>
                   <ResizablePanelGroup
                    direction="vertical"
                    className="max-w-md rounded-lg border h-72" // Example sizing
                  >
                    <ResizablePanel defaultSize={25}>
                      <div className="flex h-full items-center justify-center p-6">
                        <span className="font-semibold">Top Panel</span>
                      </div>
                    </ResizablePanel>
                    <ResizableHandle withHandle />
                    <ResizablePanel defaultSize={75}>
                      <div className="flex h-full items-center justify-center p-6">
                        <span className="font-semibold">Bottom Panel</span>
                      </div>
                    </ResizablePanel>
                  </ResizablePanelGroup>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Charts Section */}
            <TabsContent value="charts" className="space-y-8">
              {/* Existing Chart examples */}
              <Card>
                <CardHeader>
                  <CardTitle>Charts (Recharts)</CardTitle>
                  <CardDescription>Various chart types using the Recharts library</CardDescription>
                </CardHeader>
                <CardContent className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Line Chart */}
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium">Line Chart</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsLineChart data={lineData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <RechartsTooltip />
                        <Legend />
                        <Line type="monotone" dataKey="value" stroke={themeColors.primary} activeDot={{ r: 8 }} />
                      </RechartsLineChart>
                    </ResponsiveContainer>
                      </div>

                  {/* Bar Chart */}
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium">Bar Chart</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsBarChart data={barData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <RechartsTooltip />
                        <Legend />
                        <Bar dataKey="value" fill="var(--secondary)" />
                      </RechartsBarChart>
                    </ResponsiveContainer>
                      </div>

                  {/* Pie Chart */}
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium">Pie Chart</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsPieChart>
                        <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} fill="var(--accent)" label>
                            {pieData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                        <RechartsTooltip />
                        <Legend />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Area Chart */}
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium">Area Chart</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={areaData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <RechartsTooltip />
                           <Legend />
                          <Area type="monotone" dataKey="value" stroke={themeColors.primary} fill={themeColors.primary} fillOpacity={0.3} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Radar Chart */}
                   <div className="space-y-2">
                    <h3 className="text-lg font-medium">Radar Chart</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                          <PolarGrid />
                          <PolarAngleAxis dataKey="subject" />
                          <PolarRadiusAxis />
                          <Radar name="Mike" dataKey="A" stroke={themeColors.primary} fill={themeColors.primary} fillOpacity={0.6} />
                          <Radar name="Lily" dataKey="B" stroke="var(--secondary)" fill="var(--secondary)" fillOpacity={0.6} />
                           <Legend />
                           <RechartsTooltip />
                        </RadarChart>
                    </ResponsiveContainer>
                      </div>

                  {/* Scatter Chart */}
                        <div className="space-y-2">
                    <h3 className="text-lg font-medium">Scatter Chart</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <ScatterChart>
                          <CartesianGrid />
                          <XAxis type="number" dataKey="x" name="stature" unit="cm" />
                          <YAxis type="number" dataKey="y" name="weight" unit="kg" />
                          <Scatter name="A school" data={scatterData} fill="var(--accent)" />
                           <Legend />
                           <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />
                        </ScatterChart>
                    </ResponsiveContainer>
                  </div>

                </CardContent>
              </Card>
            </TabsContent>

            {/* Icons Section */}
            <TabsContent value="icons" className="space-y-8">
              <Card>
                <CardHeader>
                  <CardTitle>Icons (Lucide React)</CardTitle>
                  <CardDescription>Commonly used icons available via lucide-react</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-4">
                  {/* Display a selection of icons */}
                  {[
                    Search, Filter, BarChart4, PieChart, LineChart, Plus, Trash, Edit, Save, Download, Upload, RefreshCw, Settings, ChevronDown, ChevronUp, ArrowUpDown, X, Check, User, Home, ShoppingCart, FileText, Bell, CalendarIcon, Mail, Phone, CreditCard, HelpCircle, Info, AlertTriangle, CheckCircle, XCircle, Minus
                  ].map((Icon, index) => (
                    <div key={index} className="flex flex-col items-center p-2 border rounded-md w-20 text-center">
                      <Icon className="h-6 w-6 mb-1" />
                      <span className="text-xs truncate w-full">{Icon.displayName || 'Icon'}</span>
                    </div>
                  ))}
                  <p className="w-full text-sm text-muted-foreground mt-4">
                    See the <a href="https://lucide.dev/icons/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Lucide Icons website</a> for a full list. Import required icons directly from 'lucide-react'.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Colors Section */}
            <TabsContent value="colors" className="space-y-8">
              <Card>
                <CardHeader>
                  <CardTitle>Color Palette</CardTitle>
                  <CardDescription>Semantic colors defined via CSS variables</CardDescription>
                </CardHeader>
                <CardContent>
                  {colorCategories.map((category) => (
                     <div key={category.category} className="mb-6">
                        <h3 className="text-lg font-medium mb-3">{category.category}</h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {category.colors.map((color) => (
                            <ColorSwatch key={color.variable} name={color.name} cssVarName={color.variable} />
                        ))}
                  </div>
                        {category.category !== colorCategories[colorCategories.length - 1].category && <Separator className="mt-6" />}
                </div>
                  ))}
              </CardContent>
            </Card>
          </TabsContent>

        </Tabs>
      </div>
        </ToastProvider>
    </Container>
  );
}


// Helper component to display color swatches
interface ColorSwatchProps {
  name: string;
  cssVarName: string;
}

const ColorSwatch: React.FC<ColorSwatchProps> = ({ name, cssVarName }) => {
  // Attempt to get computed style - might not work perfectly server-side but good for client-side rendering
  // For a robust solution, you might need to parse the actual CSS or use a theme context
  const [bgColor, setBgColor] = useState('transparent');
  const [textColor, setTextColor] = useState('inherit');

  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      const computedColor = getComputedStyle(document.documentElement).getPropertyValue(cssVarName).trim();
      setBgColor(computedColor);
      // Simple contrast check (you might need a more sophisticated library for perfect contrast)
      // This is a basic heuristic
      const colorVal = computedColor.startsWith('#') ? computedColor.substring(1) : computedColor;
      const r = parseInt(colorVal.substr(0, 2), 16);
      const g = parseInt(colorVal.substr(2, 2), 16);
      const b = parseInt(colorVal.substr(4, 2), 16);
      const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
      setTextColor(luminance > 0.5 ? '#000' : '#FFF');
    }
  }, [cssVarName]);


  return (
    <div className="flex flex-col items-start">
      <div
        className="h-16 w-full rounded-md border flex items-center justify-center"
        style={{ backgroundColor: bgColor }}
        title={`CSS Variable: ${cssVarName}`}
      >
         <span style={{color: textColor}} className="text-xs font-mono mix-blend-difference p-1 rounded bg-black/10">{bgColor}</span>
      </div>
      <div className="mt-2 text-sm">{name}</div>
      <div className="text-xs text-muted-foreground">{cssVarName}</div>
  </div>
); 
};

// Add lucide icons used in new examples if they weren't already imported
import { Bold, Italic, Underline, LogOut } from 'lucide-react';

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
  Settings
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
  themeColors
} from '@/components/ui';

export default function UIComponentsPage() {
  const [activeTab, setActiveTab] = useState('buttons');

  return (
    <div className="container mx-auto py-20 px-4 md:px-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-amber-500">UI Components / Style Guide</h1>
        <p className="text-gray-400 mb-8">A collection of UI components for the pyERP system</p>

        <Tabs defaultValue="buttons" className="w-full" onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 mb-8">
            <TabsTrigger value="buttons">Buttons</TabsTrigger>
            <TabsTrigger value="inputs">Inputs</TabsTrigger>
            <TabsTrigger value="cards">Cards</TabsTrigger>
            <TabsTrigger value="tables">Tables</TabsTrigger>
            <TabsTrigger value="charts">Charts</TabsTrigger>
            <TabsTrigger value="filters">Filters</TabsTrigger>
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
                      <select className="w-full rounded-md border border-amber-800/35 bg-amber-950/25 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none">
                        <option value="option1">Option 1</option>
                        <option value="option2">Option 2</option>
                        <option value="option3">Option 3</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Textarea</label>
                      <textarea 
                        className="w-full rounded-md border border-amber-800/35 bg-amber-950/25 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none" 
                        placeholder="Enter multiple lines of text..."
                        rows={3}
                      />
                    </div>
                    <div className="flex items-center space-x-2">
                      <input 
                        type="checkbox" 
                        id="checkbox" 
                        className="h-4 w-4 rounded border-amber-800/35 text-amber-600 focus:ring-orange-500" 
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
                <CardTitle>Tables</CardTitle>
                <CardDescription>Table styles for displaying data</CardDescription>
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
                        <div className="w-16 h-16 rounded-md bg-amber-600 mr-4"></div>
                        <div>
                          <p className="font-medium">Amber 600</p>
                          <p className="text-sm text-gray-400">Primary</p>
                          <p className="text-xs text-gray-500">{themeColors.amber500}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-amber-700 mr-4"></div>
                        <div>
                          <p className="font-medium">Amber 700</p>
                          <p className="text-sm text-gray-400">Primary Hover</p>
                          <p className="text-xs text-gray-500">{themeColors.amber600}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-amber-800 mr-4"></div>
                        <div>
                          <p className="font-medium">Amber 800</p>
                          <p className="text-sm text-gray-400">Primary Active</p>
                          <p className="text-xs text-gray-500">{themeColors.amber700}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-orange-500 mr-4"></div>
                        <div>
                          <p className="font-medium">Orange 500</p>
                          <p className="text-sm text-gray-400">Focus Border</p>
                          <p className="text-xs text-gray-500">{themeColors.focusBorder}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-4">Background Colors</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-neutral-900 mr-4 border border-gray-700"></div>
                        <div>
                          <p className="font-medium">Neutral 900</p>
                          <p className="text-sm text-gray-400">Background</p>
                          <p className="text-xs text-gray-500">{themeColors.darkBg}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-amber-950/25 mr-4 border border-gray-700"></div>
                        <div>
                          <p className="font-medium">Amber 950 (25%)</p>
                          <p className="text-sm text-gray-400">Card Background</p>
                          <p className="text-xs text-gray-500">{themeColors.cardBg}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-amber-900/25 mr-4 border border-gray-700"></div>
                        <div>
                          <p className="font-medium">Amber 900 (25%)</p>
                          <p className="text-sm text-gray-400">Highlight Background</p>
                          <p className="text-xs text-gray-500">{themeColors.highlightBg}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-4">Text Colors</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-neutral-900 mr-4 flex items-center justify-center">
                          <span className="text-amber-50">Aa</span>
                        </div>
                        <div>
                          <p className="font-medium">Amber 50</p>
                          <p className="text-sm text-gray-400">Primary Text</p>
                          <p className="text-xs text-gray-500">{themeColors.lightText}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-neutral-900 mr-4 flex items-center justify-center">
                          <span className="text-amber-500">Aa</span>
                        </div>
                        <div>
                          <p className="font-medium">Amber 500</p>
                          <p className="text-sm text-gray-400">Accent Text</p>
                          <p className="text-xs text-gray-500">{themeColors.accentText}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-neutral-900 mr-4 flex items-center justify-center">
                          <span className="text-amber-200/70">Aa</span>
                        </div>
                        <div>
                          <p className="font-medium">Amber 200 (70%)</p>
                          <p className="text-sm text-gray-400">Muted Text</p>
                          <p className="text-xs text-gray-500">{themeColors.mutedText}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-4">Status Colors</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <div className="w-16 h-16 rounded-md bg-transparent mr-4 border-2 border-amber-800/35"></div>
                        <div>
                          <p className="font-medium">Amber 800 (35%)</p>
                          <p className="text-sm text-gray-400">Border</p>
                          <p className="text-xs text-gray-500">{themeColors.borderColor}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <StatusBadge status="active" className="mr-4 py-2 px-4">Active</StatusBadge>
                        <div>
                          <p className="font-medium">Green Status</p>
                          <p className="text-sm text-gray-400">Active state</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <StatusBadge status="pending" className="mr-4 py-2 px-4">Pending</StatusBadge>
                        <div>
                          <p className="font-medium">Yellow Status</p>
                          <p className="text-sm text-gray-400">Pending state</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <StatusBadge status="inactive" className="mr-4 py-2 px-4">Inactive</StatusBadge>
                        <div>
                          <p className="font-medium">Red Status</p>
                          <p className="text-sm text-gray-400">Inactive state</p>
                        </div>
                      </div>
                    </div>
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
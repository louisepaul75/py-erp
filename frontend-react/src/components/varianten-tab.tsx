"use client"

import { useState } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Plus, Minus } from "lucide-react"

export default function VariantenTab() {
  const [activeTab, setActiveTab] = useState("details")

  const variants = [
    {
      nummer: "501506",
      bezeichnung: '"Adler"-Lock',
      auspragung: "Blank",
      prod: false,
      vertr: false,
      vkArtikel: true,
      releas: "11.02.2023",
    },
    {
      nummer: "100870",
      bezeichnung: '"Adler"-Lock',
      auspragung: "Bemalt",
      prod: true,
      vertr: true,
      vkArtikel: true,
      releas: "01.01.2023",
    },
    {
      nummer: "904743",
      bezeichnung: '"Adler"-Lock OX',
      auspragung: "",
      prod: false,
      vertr: false,
      vkArtikel: false,
      releas: "01.01.1999",
    },
  ]

  return (
    <div>
      <div className="p-4">
        <div className="flex items-center gap-2 mb-4">
          <h3 className="text-sm font-medium">Varianten</h3>
          <Button variant="outline" size="icon" className="h-6 w-6">
            <Plus className="h-3 w-3" />
          </Button>
          <Button variant="outline" size="icon" className="h-6 w-6">
            <Minus className="h-3 w-3" />
          </Button>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nummer</TableHead>
              <TableHead>Bezeichnung</TableHead>
              <TableHead>Ausprägung</TableHead>
              <TableHead className="w-12 text-center">Prod.</TableHead>
              <TableHead className="w-12 text-center">Vertr.</TableHead>
              <TableHead className="w-12 text-center">VK Artikel</TableHead>
              <TableHead>Releas</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {variants.map((variant, index) => (
              <TableRow key={variant.nummer} className={index === 1 ? "bg-blue-100" : ""}>
                <TableCell>{variant.nummer}</TableCell>
                <TableCell>{variant.bezeichnung}</TableCell>
                <TableCell>{variant.auspragung}</TableCell>
                <TableCell className="text-center">
                  <input type="checkbox" checked={variant.prod} readOnly />
                </TableCell>
                <TableCell className="text-center">
                  <input type="checkbox" checked={variant.vertr} readOnly />
                </TableCell>
                <TableCell className="text-center">
                  <input type="checkbox" checked={variant.vkArtikel} readOnly />
                </TableCell>
                <TableCell>{variant.releas}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="border-t">
        <Tabs defaultValue="details" value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="bg-gray-100 border-b p-0 h-auto rounded-none">
            <TabsTrigger
              value="details"
              className="px-4 py-2 rounded-none data-[state=active]:bg-white data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none"
            >
              Details
            </TabsTrigger>
            <TabsTrigger
              value="teile"
              className="px-4 py-2 rounded-none data-[state=active]:bg-white data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none"
            >
              Teile
            </TabsTrigger>
            <TabsTrigger
              value="bilder"
              className="px-4 py-2 rounded-none data-[state=active]:bg-white data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none"
            >
              Bilder
            </TabsTrigger>
            <TabsTrigger
              value="gewogen"
              className="px-4 py-2 rounded-none data-[state=active]:bg-white data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none"
            >
              Gewogen
            </TabsTrigger>
            <TabsTrigger
              value="lagerorte"
              className="px-4 py-2 rounded-none data-[state=active]:bg-white data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none"
            >
              Lagerorte
            </TabsTrigger>
            <TabsTrigger
              value="umsatze"
              className="px-4 py-2 rounded-none data-[state=active]:bg-white data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none"
            >
              Umsätze
            </TabsTrigger>
            <TabsTrigger
              value="bewegungen"
              className="px-4 py-2 rounded-none data-[state=active]:bg-white data-[state=active]:border-t-2 data-[state=active]:border-t-blue-500 data-[state=active]:shadow-none"
            >
              Bewegungen
            </TabsTrigger>
          </TabsList>

          <TabsContent value="details" className="p-4 m-0">
            <div className="mb-4">
              <div className="flex items-center gap-2 mb-4">
                <h3 className="text-sm font-medium">Kategorien</h3>
                <Button variant="outline" size="icon" className="h-6 w-6">
                  <Plus className="h-3 w-3" />
                </Button>
                <Button variant="outline" size="icon" className="h-6 w-6">
                  <Minus className="h-3 w-3" />
                </Button>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Home</TableHead>
                    <TableHead>Sortiment</TableHead>
                    <TableHead>Tradition</TableHead>
                    <TableHead>Maschinerie</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell>Home</TableCell>
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                    <TableCell>All Products</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="lagerorte" className="p-0 m-0">
            <LagerorteContent />
          </TabsContent>

          <TabsContent value="gewogen" className="p-0 m-0">
            <GewogenContent />
          </TabsContent>

          <TabsContent value="umsatze" className="p-0 m-0">
            <UmsatzeContent />
          </TabsContent>

          <TabsContent value="bewegungen" className="p-0 m-0">
            <BewegungenContent />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

function LagerorteContent() {
  return (
    <div className="p-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Lager</TableHead>
            <TableHead>Regal</TableHead>
            <TableHead>Fach</TableHead>
            <TableHead>Boden</TableHead>
            <TableHead>Schütte</TableHead>
            <TableHead>Slot(s)</TableHead>
            <TableHead>Abverkauf</TableHead>
            <TableHead>Sonder</TableHead>
            <TableHead>Bestand</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>18187 / Stammlager-Dies...</TableCell>
            <TableCell>23</TableCell>
            <TableCell>1</TableCell>
            <TableCell>6</TableCell>
            <TableCell>SC832607</TableCell>
            <TableCell>MZ</TableCell>
            <TableCell className="text-center">
              <input type="checkbox" checked readOnly />
            </TableCell>
            <TableCell className="text-center">
              <input type="checkbox" readOnly />
            </TableCell>
            <TableCell>0</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>18187 / Stammlager-Dies...</TableCell>
            <TableCell>23</TableCell>
            <TableCell>1</TableCell>
            <TableCell>6</TableCell>
            <TableCell>SC832607</TableCell>
            <TableCell>MZ</TableCell>
            <TableCell className="text-center">
              <input type="checkbox" checked readOnly />
            </TableCell>
            <TableCell className="text-center">
              <input type="checkbox" readOnly />
            </TableCell>
            <TableCell>0</TableCell>
          </TableRow>
          {[...Array(15)].map((_, i) => (
            <TableRow key={i}>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
            </TableRow>
          ))}
          <TableRow>
            <TableCell></TableCell>
            <TableCell></TableCell>
            <TableCell></TableCell>
            <TableCell></TableCell>
            <TableCell></TableCell>
            <TableCell></TableCell>
            <TableCell></TableCell>
            <TableCell></TableCell>
            <TableCell>0</TableCell>
          </TableRow>
        </TableBody>
      </Table>
      <div className="flex gap-2 mt-4">
        <Button variant="outline">Bestand ändern</Button>
        <Button variant="outline">Umbuchen</Button>
      </div>
    </div>
  )
}

function GewogenContent() {
  return (
    <div className="p-4">
      <div className="flex items-center gap-2 mb-6">
        <label className="text-sm font-medium">Gewicht</label>
        <input type="text" className="border rounded w-16 px-2 py-1 text-right" defaultValue="0" />
      </div>

      <div className="flex gap-8">
        <div className="flex-1">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Datum</TableHead>
                <TableHead>Zeit</TableHead>
                <TableHead>g</TableHead>
                <TableHead>Stück</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[...Array(12)].map((_, i) => (
                <TableRow key={i}>
                  <TableCell></TableCell>
                  <TableCell></TableCell>
                  <TableCell></TableCell>
                  <TableCell></TableCell>
                </TableRow>
              ))}
              <TableRow>
                <TableCell>0</TableCell>
                <TableCell></TableCell>
                <TableCell>0</TableCell>
                <TableCell>0</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>

        <div className="w-72">
          <div className="mb-4">
            <div className="text-sm mb-1">Durchschnittsgewicht:</div>
            <div className="text-lg font-medium">0 g</div>
          </div>
          <div className="mb-4">
            <div className="text-sm mb-1">Standardabweichung:</div>
            <div className="text-lg font-medium">0,00 g</div>
            <div className="text-lg font-medium">0,00 %</div>
          </div>
          <Button variant="outline" className="w-full">
            Ø übernehmen
          </Button>
        </div>
      </div>
    </div>
  )
}

function UmsatzeContent() {
  return (
    <div className="p-4">
      <div className="flex gap-8">
        <div className="flex-1">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Jahr</TableHead>
                <TableHead>Vorjahr</TableHead>
                <TableHead>5 Jahre</TableHead>
                <TableHead>Gesamt</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Stück</TableCell>
                <TableCell>0</TableCell>
                <TableCell>3</TableCell>
                <TableCell>13</TableCell>
                <TableCell>16</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">EUR</TableCell>
                <TableCell>0,00</TableCell>
                <TableCell>76,20</TableCell>
                <TableCell>455,00</TableCell>
                <TableCell>561,30</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>

        <div className="w-72 border p-3 rounded">
          <h3 className="text-sm font-medium mb-2">Lager</h3>
          <div className="grid grid-cols-2 gap-y-2">
            <div className="text-sm">Bestand</div>
            <div className="text-sm text-right bg-blue-50 px-2">6</div>
            <div className="text-sm">Min. Bestand</div>
            <div className="text-sm text-right bg-yellow-50 px-2">2</div>
            <div className="text-sm">Zugang/Jahr</div>
            <div className="text-sm text-right bg-blue-50 px-2">0</div>
            <div className="text-sm">letzter Zugang</div>
            <div className="text-sm text-right bg-blue-50 px-2">22.05.2023</div>
            <div className="text-sm">Abgänge ges.</div>
            <div className="text-sm text-right bg-blue-50 px-2">19</div>
            <div className="text-sm">letzter Abgang</div>
            <div className="text-sm text-right bg-blue-50 px-2">22.10.2024</div>
          </div>
        </div>
      </div>
    </div>
  )
}

function BewegungenContent() {
  return (
    <div className="p-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Kunden-Nr</TableHead>
            <TableHead>Kunde</TableHead>
            <TableHead>Art</TableHead>
            <TableHead>Beleg-Nr</TableHead>
            <TableHead>Datum</TableHead>
            <TableHead>Menge</TableHead>
            <TableHead>Preis</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>1891810</TableCell>
            <TableCell>ADK</TableCell>
            <TableCell>L</TableCell>
            <TableCell>202060</TableCell>
            <TableCell>22.10.2024</TableCell>
            <TableCell>1</TableCell>
            <TableCell>66,70</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>1440011</TableCell>
            <TableCell>E.&A. vor dem Brocke Mackenbrock G...</TableCell>
            <TableCell>R</TableCell>
            <TableCell>2010292</TableCell>
            <TableCell>23.09.2024</TableCell>
            <TableCell>1</TableCell>
            <TableCell>27,80</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>1440011</TableCell>
            <TableCell>E.&A. vor dem Brocke Mackenbrock G...</TableCell>
            <TableCell>A</TableCell>
            <TableCell>210870</TableCell>
            <TableCell>18.09.2024</TableCell>
            <TableCell>1</TableCell>
            <TableCell>27,80</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>DE20060</TableCell>
            <TableCell>Tropp</TableCell>
            <TableCell>A</TableCell>
            <TableCell>210688</TableCell>
            <TableCell>06.08.2024</TableCell>
            <TableCell>1</TableCell>
            <TableCell>24,20</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>DE20060</TableCell>
            <TableCell>Tropp</TableCell>
            <TableCell>A</TableCell>
            <TableCell>210689</TableCell>
            <TableCell>06.08.2024</TableCell>
            <TableCell>1</TableCell>
            <TableCell>24,20</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>128017</TableCell>
            <TableCell>Tropp</TableCell>
            <TableCell>A</TableCell>
            <TableCell>210690</TableCell>
            <TableCell>06.08.2024</TableCell>
            <TableCell>1</TableCell>
            <TableCell>52,30</TableCell>
          </TableRow>
        </TableBody>
      </Table>
      <div className="flex items-center mt-2">
        <input type="checkbox" id="nur-r" />
        <label htmlFor="nur-r" className="ml-2">
          Nur R
        </label>
      </div>
    </div>
  )
}


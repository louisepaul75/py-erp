"use client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CheckCircle, Loader2, Scale, ArrowLeft, ScanBarcode, Weight } from "lucide-react"

// Mock data for bins
export const mockBins = [
  { id: "BIN001", name: "Small Bin", weight: 1.2 },
  { id: "BIN002", name: "Medium Bin", weight: 2.5 },
  { id: "BIN003", name: "Large Bin", weight: 3.8 },
]

interface WeighingProcessProps {
  scaleStep: "scan" | "tara" | "weigh" | "result"
  binId: string
  setBinId: (id: string) => void
  taraType: "manual" | "auto"
  setTaraType: (type: "manual" | "auto") => void
  manualTara: number | ""
  setManualTara: (tara: number | "") => void
  weighResult: number | null
  calculatedQuantity: number
  isMeasuringTara: boolean
  onBinScan: () => void
  onTaraSelection: (type: "manual" | "auto") => void
  onMeasureTara: () => void
  onWeighing: () => void
  onQuantityAccept: () => void
  onBack: (step: "scan" | "tara") => void
}

export function WeighingProcess({
  scaleStep,
  binId,
  setBinId,
  taraType,
  setTaraType,
  manualTara,
  setManualTara,
  weighResult,
  calculatedQuantity,
  isMeasuringTara,
  onBinScan,
  onTaraSelection,
  onMeasureTara,
  onWeighing,
  onQuantityAccept,
  onBack,
}: WeighingProcessProps) {
  const bin = mockBins.find((b) => b.id === binId)

  switch (scaleStep) {
    case "scan":
      return (
        <Card className="mt-4">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center">
              <ScanBarcode className="h-4 w-4 mr-2" />
              Step 1: Scan Bin
            </CardTitle>
            <CardDescription>Scan the bin containing the items</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-2">
              <Input
                value={binId}
                onChange={(e) => setBinId(e.target.value)}
                placeholder="Scan bin ID..."
                className="flex-1"
              />
              <Button onClick={onBinScan} disabled={!binId}>
                Next
              </Button>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              Available bins (for testing): BIN001, BIN002, BIN003
            </div>
          </CardContent>
        </Card>
      )

    case "tara":
      return (
        <Card className="mt-4">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center">
              <Weight className="h-4 w-4 mr-2" />
              Step 2: Choose Tara Method
            </CardTitle>
            <CardDescription>{bin ? `Bin: ${bin.name} (${bin.id})` : `Bin: ${binId}`}</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="auto" onValueChange={(v) => onTaraSelection(v as "manual" | "auto")}>
              <TabsList className="w-full">
                <TabsTrigger value="auto" className="flex-1">
                  Auto Tara
                </TabsTrigger>
                <TabsTrigger value="manual" className="flex-1">
                  Manual Tara
                </TabsTrigger>
              </TabsList>
              <TabsContent value="auto" className="pt-4">
                {bin ? (
                  <div className="text-sm">
                    <p>
                      Stored bin weight: <span className="font-medium">{bin.weight} kg</span>
                    </p>
                    <p className="text-muted-foreground mt-1">The bin weight will be automatically subtracted.</p>
                  </div>
                ) : (
                  <div className="text-sm text-amber-600">
                    No weight data found for this bin. Please use manual tara.
                  </div>
                )}
              </TabsContent>
              <TabsContent value="manual" className="pt-4">
                <div className="space-y-2">
                  <Label htmlFor="manual-tara">Tara weight (kg)</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="manual-tara"
                      type="number"
                      step="0.1"
                      min="0"
                      value={manualTara}
                      onChange={(e) => setManualTara(e.target.value === "" ? "" : Number(e.target.value))}
                      placeholder="0.0"
                      className="flex-1"
                    />
                    <Button onClick={onMeasureTara} disabled={isMeasuringTara} variant="secondary">
                      {isMeasuringTara ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <Weight className="h-4 w-4 mr-2" />
                      )}
                      Weigh Tara
                    </Button>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" onClick={() => onBack("scan")}>
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back
            </Button>
            <Button
              onClick={onWeighing}
              disabled={taraType === "manual" && (manualTara === "" || Number(manualTara) <= 0)}
            >
              Start Weighing
            </Button>
          </CardFooter>
        </Card>
      )

    case "weigh":
      return (
        <Card className="mt-4">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center">
              <Scale className="h-4 w-4 mr-2" />
              Step 3: Weighing in Progress
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center py-6">
            <Loader2 className="h-8 w-8 animate-spin mb-4" />
            <p>Please wait while the weighing is in progress...</p>
          </CardContent>
        </Card>
      )

    case "result":
      return (
        <Card className="mt-4">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center">
              <CheckCircle className="h-4 w-4 mr-2" />
              Weighing Complete
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Gross weight:</span>
                <span>{weighResult?.toFixed(2)} kg</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Tara:</span>
                <span>
                  {taraType === "auto" && bin
                    ? bin.weight.toFixed(2)
                    : typeof manualTara === "number"
                      ? manualTara.toFixed(2)
                      : "0.00"}{" "}
                  kg
                </span>
              </div>
              <div className="flex justify-between font-medium border-t pt-2 mt-2">
                <span>Calculated quantity:</span>
                <Badge className="ml-auto text-base px-3 py-1">{calculatedQuantity} pieces</Badge>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" onClick={() => onBack("tara")}>
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back
            </Button>
            <Button onClick={onQuantityAccept} variant="default" className="bg-black text-white hover:bg-gray-800">
              Accept Quantity
            </Button>
          </CardFooter>
        </Card>
      )

    default:
      return null
  }
}


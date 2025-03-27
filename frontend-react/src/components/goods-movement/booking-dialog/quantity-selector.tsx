"use client"

import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, Scale } from "lucide-react"
import { WeighingProcess } from "./weighing-process"

interface QuantitySelectorProps {
  quantityType: "all" | "scale" | "manual"
  setQuantityType: (type: "all" | "scale" | "manual") => void
  manualQuantity: number | ""
  setManualQuantity: (quantity: number | "") => void
  itemQuantity: number
  calculatedQuantity: number
  scaleStep: "scan" | "tara" | "weigh" | "result"
  weighingProps: any // Pass all weighing process props
}

export function QuantitySelector({
  quantityType,
  setQuantityType,
  manualQuantity,
  setManualQuantity,
  itemQuantity,
  calculatedQuantity,
  scaleStep,
  weighingProps,
}: QuantitySelectorProps) {
  return (
    <div>
      <RadioGroup
        value={quantityType}
        onValueChange={(value) => {
          setQuantityType(value as "all" | "scale" | "manual")
          if (value === "scale" && scaleStep === "scan") {
            // Start the weighing process when "Use Scale" is selected
            weighingProps.resetScaleProcess()
          }
        }}
        className="space-y-2"
      >
        <div className="flex items-center space-x-2 bg-background p-2 rounded-md border hover:bg-muted/50 transition-colors">
          <RadioGroupItem value="all" id="all" />
          <Label htmlFor="all" className="flex items-center">
            <CheckCircle className="h-4 w-4 mr-2" />
            All ({itemQuantity} pieces)
          </Label>
        </div>

        <div className="flex items-center space-x-2 bg-background p-2 rounded-md border hover:bg-muted/50 transition-colors">
          <RadioGroupItem value="scale" id="scale" />
          <Label htmlFor="scale" className="flex items-center">
            <Scale className="h-4 w-4 mr-2" />
            Use Scale
            {quantityType === "scale" && calculatedQuantity > 0 && (
              <Badge variant="outline" className="ml-2">
                {calculatedQuantity} pieces
              </Badge>
            )}
          </Label>
        </div>

        <div className="flex items-center space-x-2 bg-background p-2 rounded-md border hover:bg-muted/50 transition-colors">
          <RadioGroupItem value="manual" id="manual" />
          <Label htmlFor="manual" className="flex-grow">
            Manual Entry
          </Label>
          <Input
            id="manual-quantity"
            type="number"
            min="1"
            max={itemQuantity}
            value={manualQuantity}
            onChange={(e) => {
              const value = e.target.value === "" ? "" : Number.parseInt(e.target.value, 10)
              setManualQuantity(value)
              setQuantityType("manual")
            }}
            disabled={quantityType !== "manual"}
            className="w-20"
          />
        </div>
      </RadioGroup>

      {/* Weighing process */}
      {quantityType === "scale" && (
        <WeighingProcess
          scaleStep={scaleStep}
          binId={weighingProps.binId}
          setBinId={weighingProps.setBinId}
          taraType={weighingProps.taraType}
          setTaraType={weighingProps.setTaraType}
          manualTara={weighingProps.manualTara}
          setManualTara={weighingProps.setManualTara}
          weighResult={weighingProps.weighResult}
          calculatedQuantity={calculatedQuantity}
          isMeasuringTara={weighingProps.isMeasuringTara}
          onBinScan={weighingProps.handleBinScan}
          onTaraSelection={weighingProps.handleTaraSelection}
          onMeasureTara={weighingProps.handleMeasureTara}
          onWeighing={weighingProps.handleWeighing}
          onQuantityAccept={weighingProps.handleQuantityAccept}
          onBack={weighingProps.handleScaleBack}
        />
      )}
    </div>
  )
}


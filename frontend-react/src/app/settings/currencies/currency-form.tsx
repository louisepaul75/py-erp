"use client"

import { useEffect } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { useCurrencyContext } from "./currency-provider"
import { useAddCurrency, useCurrenciesList, useUpdateCurrency, useFetchExchangeRate } from "@/hooks/use-currencies"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { toast } from "@/hooks/use-toast"
import { RefreshCw } from "lucide-react"
import useAppTranslation from "@/hooks/useTranslationWrapper"


const currencyFormSchema = z.object({
  code: z.string().length(3, "Währungscode muss genau 3 Zeichen lang sein"),
  name: z.string().min(2, "Name muss mindestens 2 Zeichen lang sein"),
  realTimeRate: z.coerce.number().positive("Kurs muss positiv sein"),
  calculationRate: z.coerce.number().positive("Kurs muss positiv sein"),
})

type CurrencyFormValues = z.infer<typeof currencyFormSchema>

export default function CurrencyForm() {
  const { selectedCurrency, isAddingCurrency, setIsAddingCurrency } = useCurrencyContext()
  const addCurrency = useAddCurrency()
  const updateCurrency = useUpdateCurrency()
  const { data: showCurrencyList = [], isLoading } = useCurrenciesList();
  const { fetchRate, isLoading: isFetchingRate } = useFetchExchangeRate()

  const { t } = useAppTranslation("settings_currency");
  
  const form = useForm<CurrencyFormValues>({
    resolver: zodResolver(currencyFormSchema),
    defaultValues: {
      code: "",
      name: "",
      realTimeRate: 1,
      calculationRate: 1,
    },
  })

  useEffect(() => {
    if (selectedCurrency) {
      form.reset({
        code: selectedCurrency.code,
        name: selectedCurrency.name,
        realTimeRate: selectedCurrency.realTimeRate,
        calculationRate: selectedCurrency.calculationRate,
      })
    } else {
      form.reset({
        code: "",
        name: "",
        realTimeRate: 1,
        calculationRate: 1,
      })
    }
  }, [selectedCurrency, form])

  const onSubmit = async (data: CurrencyFormValues) => {
    try {
      if (selectedCurrency) {
        await updateCurrency.mutateAsync({
          id: selectedCurrency.id,
          ...data,
        })
        toast({
          title: t("currency_updated"),
          description: `${data.name} (${data.code}) ${t("was_successfully_updated")}`,
        })
      } else {

        await addCurrency.mutateAsync(data)
        console.log("addCurrency", addCurrency)
        toast({
          title:  t("currency_added"),
          description: `${data.name} (${data.code}) ${t("was_successfully_added")}`,
        })
      }
      // setIsAddingCurrency(false)
    } catch (error) {
      toast({
        title: t("error"),
        description: t("save_currency_error"),
        variant: "destructive",
      })
    }
  }

  // Füge eine spezielle Behandlung für EUR im handleFetchRate hinzu
  const handleFetchRate = async () => {
    const code = form.getValues("code")
    if (code.length !== 3) {
      toast({
        title: t("error"),
        description:  t("fetch_rate_error"),
        variant: "destructive",
      })
      return
    }

    // Wenn es sich um EUR handelt, setze den Kurs auf 1
    if (code.toUpperCase() === "EUR") {
      form.setValue("realTimeRate", 1.0)
      form.setValue("calculationRate", 1.0)
      toast({
        title: t("hint"),
        description: t("euro_base_currency"),
      })
      return
    }

    console.log("handleFetchRate", code)
    try {
      let rate = null;
      const eurCurrency = showCurrencyList.find((currency) => currency.code === "EUR");
      if (eurCurrency) {
        const match = eurCurrency.exchange_rates.find(
          (exchange_rate) => exchange_rate.target_currency?.includes(code)
        );

        rate = match?.rate ?? null;
      }
      form.setValue("realTimeRate", rate)
      form.setValue("calculationRate", rate)

      toast({
        title: t("rate_updated"),
        description: `${t("the_current_rate_for")} ${code} t("was_successfully_retrieved")}`,
      })
    } catch (error) {
      toast({
        title: t("error"),
        description: t("fetch_rate_error_message"),
        variant: "destructive",
      })
    }
  }

  return (
    <Dialog open={isAddingCurrency} onOpenChange={setIsAddingCurrency}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{selectedCurrency ? "Währung bearbeiten" : "Neue Währung hinzufügen"}</DialogTitle>
          <DialogDescription>
            {selectedCurrency
              ? t("edit_currency_description")
              : t("add_currency_description")}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("currency_code")}</FormLabel>
                    <Select
                      onValueChange={(val) => {
                        field.onChange(val)
                        const selected = showCurrencyList.find((opt) => opt.code === val)
                        if (selected) {
                          form.setValue("name", selected.name)
                          form.setValue("code", selected.code)
                          handleFetchRate()
                        }
                      }}
                      value={field.value}
                      disabled={!!selectedCurrency}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="EUR" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {showCurrencyList?.map((currency) => (
                          <SelectItem key={currency.code} value={currency.code}>
                            {currency.code}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>{t("currency_code_description")}</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t("currency_name")}</FormLabel>
                    <FormControl>
                      <Input placeholder="Euro" {...field} />
                    </FormControl>
                    <FormDescription>{t("currency_name_description")}</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="realTimeRate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t("real_time_rate")}</FormLabel>
                    <div className="flex gap-2">
                      <FormControl>
                        <Input type="number" step="0.0001" min="0" placeholder="1.0000" {...field} />
                      </FormControl>
                      <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        onClick={handleFetchRate}
                        disabled={isFetchingRate}
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                    </div>
                    <FormDescription>{t("real_time_rate_description")}</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="calculationRate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t("calculation_rate")}</FormLabel>
                    <FormControl>
                      <Input type="number" step="0.0001" min="0" placeholder="1.0000" {...field} />
                    </FormControl>
                    <FormDescription>{t("calculation_rate_description")}</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsAddingCurrency(false)}>
              {t("cancel")}
              </Button>
              <Button type="submit" disabled={addCurrency.isPending || updateCurrency.isPending}>
                {addCurrency.isPending || updateCurrency.isPending
                  ? t("is_being_saved")
                  : selectedCurrency
                    ? t("refresh")
                    : t("add")}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

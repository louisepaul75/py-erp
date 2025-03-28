export interface CurrencyHistoryPoint {
  date: string
  rate: number
}

export interface CurrencyHistory {
  currencyId: string
  currencyCode: string
  history: CurrencyHistoryPoint[]
}

export type TimeRange = "day" | "week" | "month" | "quarter" | "year"


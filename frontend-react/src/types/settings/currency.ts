export interface Currency {
  id: string
  code: string
  name: string
  realTimeRate: number
  calculationRate: number
  lastUpdated: string
}

export interface CurrencyInput {
  code: string
  name: string
  realTimeRate: number
  calculationRate: number
}

export interface CurrencyUpdateInput extends CurrencyInput {
  id: string
}


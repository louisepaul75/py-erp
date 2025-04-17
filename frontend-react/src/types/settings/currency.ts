export interface Currency {
  id: string
  code: string
  name: string
  realTimeRate: number
  calculationRate: number
  lastUpdated: string
}

type ExchangeRate = {
  target_currency: string;
  rate: string;
  date: string;
};

export interface CurrencyList {
  code: string
  name: string
  exchange_rates: ExchangeRate[];
}

export interface CurrencyInput {
  code: string
  name: string
  realTimeRate: number
  calculationRate: number
}

export interface CurrencyUpdateInput extends CurrencyInput {
  id: string
  code: string
  name: string
  realTimeRate: number
  calculationRate: number
}


import { Skeleton } from "@/components/ui/skeleton"

export function PicklistSkeleton() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <Skeleton className="h-10 w-[300px]" />
          <Skeleton className="h-10 w-[180px]" />
        </div>
        <Skeleton className="h-10 w-full md:w-[300px]" />
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <Skeleton className="h-5 w-[150px]" />
        <Skeleton className="h-10 w-[200px]" />
      </div>

      <div className="rounded-md border">
        <div className="overflow-x-auto">
          <Skeleton className="h-[500px] w-full" />
        </div>
      </div>
    </div>
  )
}


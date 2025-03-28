import { NextResponse, type NextRequest } from 'next/server'

export async function GET() {
  return NextResponse.json({ message: 'Cookie endpoint' })
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    return NextResponse.json({ message: 'Cookie set successfully', data: body })
  } catch (error) {
    return NextResponse.json({ message: 'Failed to set cookie', error: error instanceof Error ? error.message : 'Unknown error' }, { status: 400 })
  }
}

export async function DELETE() {
  return NextResponse.json({ message: 'Cookie deleted successfully' })
} 
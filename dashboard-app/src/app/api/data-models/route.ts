import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { NextRequest, NextResponse } from "next/server"

/**
 * GET /api/data-models
 * List all data models with their relationships
 */
export async function GET(req: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const models = await prisma.dataModel.findMany({
      include: {
        source_relationships: {
          include: { target_model: true },
        },
        target_relationships: {
          include: { source_model: true },
        },
      },
      orderBy: { name: "asc" },
    })

    // Parse schema_json for each model
    const parsed = models.map((m) => ({
      id: m.id,
      name: m.name,
      version: m.version,
      columns: parseSchemaColumns(m.schema_json),
      relationships: {
        outbound: m.source_relationships.map((r) => ({
          id: r.id,
          type: r.type,
          targetModel: r.target_model.name,
        })),
        inbound: m.target_relationships.map((r) => ({
          id: r.id,
          type: r.type,
          sourceModel: r.source_model.name,
        })),
      },
    }))

    return NextResponse.json(parsed)
  } catch (error) {
    console.error("Error fetching data models:", error)
    return NextResponse.json(
      { error: "Failed to fetch data models" },
      { status: 500 }
    )
  }
}

function parseSchemaColumns(schemaJson: string): string[] {
  try {
    const schema = JSON.parse(schemaJson || "{}")
    if (schema.columns && Array.isArray(schema.columns)) {
      return schema.columns.map((c: any) => c.name || c)
    }
    if (schema.fields && Array.isArray(schema.fields)) {
      return schema.fields.map((f: any) => f.name || f)
    }
    // fallback: return keys if schema is an object
    return Object.keys(schema)
  } catch (e) {
    return []
  }
}

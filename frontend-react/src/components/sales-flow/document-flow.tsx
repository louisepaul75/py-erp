"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import ReactFlow, {
  Background,
  Controls,
  type Edge,
  type Node,
  type NodeTypes,
  useEdgesState,
  useNodesState,
  useReactFlow,
  ReactFlowProvider,
  Panel,
} from "reactflow"
import "reactflow/dist/style.css"
import { useDocumentGraph } from "@/hooks/document/use-document-graph"
import { DocumentNode } from "@/components/sales-flow/document-node"
import { Button } from "@/components/ui/button"
import { ZoomIn, ZoomOut, LayoutGrid, List, BarChart } from "lucide-react"
import { useMediaQuery } from "@/hooks/document/use-media-query"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useDocuments } from "@/hooks/document/use-documents"
import dagre from "dagre"
import { DocumentFlowTable } from "@/components/sales-flow/document-flow-table"

/**
 * Node width and height for layout calculations
 */
const NODE_WIDTH = 220
const NODE_HEIGHT = 150

/**
 * Props for the DocumentFlow component
 */
interface DocumentFlowProps {
  initialDocumentId?: string // Optional: If provided, this document will be pre-selected
}

/**
 * Function to calculate layout using dagre
 */
const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = "TB") => {
  // Create a new dagre graph
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))

  // Set graph direction and node dimensions
  dagreGraph.setGraph({ rankdir: direction })

  // Add nodes to the graph
  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT })
  })

  // Add edges to the graph
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  // Calculate the layout
  dagre.layout(dagreGraph)

  // Apply the calculated positions to the nodes
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)

    return {
      ...node,
      position: {
        x: nodeWithPosition.x - NODE_WIDTH / 2,
        y: nodeWithPosition.y - NODE_HEIGHT / 2,
      },
    }
  })

  return { nodes: layoutedNodes, edges }
}

/**
 * Custom node types for the flow diagram
 */
const nodeTypes: NodeTypes = {
  documentNode: DocumentNode,
}

/**
 * Inner component that contains the actual flow diagram
 * This is separated to use the React Flow hooks inside the provider
 */
function DocumentFlowInner({ initialDocumentId }: DocumentFlowProps) {
  // Fetch all documents
  const { data: allDocuments } = useDocuments()

  // State for the selected document
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(initialDocumentId || null)

  // State for the view mode (graph or table)
  const [viewMode, setViewMode] = useState<"graph" | "table">("table")

  // Fetch document graph data using TanStack Query
  const { data: fullGraphData, isLoading, isError } = useDocumentGraph()

  // React Flow states
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  // State for the selected node
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  // React Flow instance
  const reactFlowInstance = useReactFlow()

  // Ref to track if initial layout has been applied
  const initialLayoutApplied = useRef(false)

  // Check if the device is a tablet or mobile
  const isTablet = useMediaQuery("(max-width: 1024px)")

  // Function to apply auto layout
  const onLayout = useCallback(
    (direction: "TB" | "LR" = "TB") => {
      if (!nodes.length) return

      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(nodes, edges, direction)

      setNodes([...layoutedNodes])

      // Give the nodes time to update before fitting the view
      window.requestAnimationFrame(() => {
        reactFlowInstance.fitView({ padding: 0.2 })
      })
    },
    [nodes, edges, setNodes, reactFlowInstance],
  )

  // Filter graph data to only show documents connected to the selected document
  useEffect(() => {
    if (fullGraphData && selectedDocumentId) {
      // Find all connected documents (direct and indirect connections)
      const connectedDocIds = new Set<string>([selectedDocumentId])
      let newIdsFound = true

      // Keep looking for connections until no new connections are found
      while (newIdsFound) {
        newIdsFound = false

        fullGraphData.relationships.forEach((rel) => {
          if (connectedDocIds.has(rel.sourceId) && !connectedDocIds.has(rel.targetId)) {
            connectedDocIds.add(rel.targetId)
            newIdsFound = true
          }
          if (connectedDocIds.has(rel.targetId) && !connectedDocIds.has(rel.sourceId)) {
            connectedDocIds.add(rel.sourceId)
            newIdsFound = true
          }
        })
      }

      // Filter nodes and edges
      const filteredDocuments = fullGraphData.documents.filter((doc) => connectedDocIds.has(doc.id))
      const filteredRelationships = fullGraphData.relationships.filter(
        (rel) => connectedDocIds.has(rel.sourceId) && connectedDocIds.has(rel.targetId),
      )

      // Create nodes from document data
      const graphNodes: Node[] = filteredDocuments.map((doc) => ({
        id: doc.id,
        type: "documentNode",
        position: doc.position || { x: 0, y: 0 },
        data: {
          ...doc,
          selected: selectedNode === doc.id,
          onSelect: () => setSelectedNode(doc.id),
        },
      }))

      // Create edges from relationship data
      const graphEdges: Edge[] = filteredRelationships.map((rel) => ({
        id: rel.id,
        source: rel.sourceId,
        target: rel.targetId,
        label: rel.type,
        type: "smoothstep",
        animated: true,
        style: { stroke: "#888" },
      }))

      setNodes(graphNodes)
      setEdges(graphEdges)

      // Reset the layout flag when data changes
      initialLayoutApplied.current = false
    } else if (fullGraphData && !selectedDocumentId) {
      // If no document is selected, show all documents
      const graphNodes: Node[] = fullGraphData.documents.map((doc) => ({
        id: doc.id,
        type: "documentNode",
        position: doc.position || { x: 0, y: 0 },
        data: {
          ...doc,
          selected: selectedNode === doc.id,
          onSelect: () => setSelectedNode(doc.id),
        },
      }))

      const graphEdges: Edge[] = fullGraphData.relationships.map((rel) => ({
        id: rel.id,
        source: rel.sourceId,
        target: rel.targetId,
        label: rel.type,
        type: "smoothstep",
        animated: true,
        style: { stroke: "#888" },
      }))

      setNodes(graphNodes)
      setEdges(graphEdges)

      // Reset the layout flag when data changes
      initialLayoutApplied.current = false
    }
  }, [fullGraphData, selectedDocumentId, selectedNode, setNodes, setEdges])

  // Apply initial layout once after nodes are set
  useEffect(() => {
    if (nodes.length > 0 && !initialLayoutApplied.current && viewMode === "graph") {
      // Set the flag to true to prevent repeated layouts
      initialLayoutApplied.current = true

      // Apply the layout with a small delay to ensure nodes are properly rendered
      const timer = setTimeout(() => {
        onLayout()
      }, 100)

      return () => clearTimeout(timer)
    }
  }, [nodes, onLayout, viewMode])

  // Handle zoom in
  const handleZoomIn = () => {
    reactFlowInstance.zoomIn()
  }

  // Handle zoom out
  const handleZoomOut = () => {
    reactFlowInstance.zoomOut()
  }

  // Handle document selection change
  const handleDocumentChange = (documentId: string) => {
    setSelectedDocumentId(documentId)
    setSelectedNode(documentId)
  }

  // Get selected document details
  const selectedDocument = allDocuments?.find((doc) => doc.id === selectedDocumentId)

  // Loading state
  if (isLoading) {
    return <div className="flex justify-center p-8">Dokumentenbeziehungen werden geladen...</div>
  }

  // Error state
  if (isError) {
    return <div className="flex justify-center p-8 text-red-500">Fehler beim Laden der Dokumentenbeziehungen</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="flex-1">
          <Select value={selectedDocumentId || ""} onValueChange={handleDocumentChange}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Dokument auswählen">
                {selectedDocument
                  ? `${selectedDocument.type} - ${selectedDocument.number} - ${selectedDocument.customer.name}`
                  : "Dokument auswählen"}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {allDocuments?.map((doc) => (
                <SelectItem key={doc.id} value={doc.id}>
                  {doc.type} - {doc.number} - {doc.customer.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2 ml-4">
          <Button
            variant={viewMode === "graph" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("graph")}
            className="flex items-center gap-2"
          >
            <BarChart className="h-4 w-4" />
            <span className="hidden sm:inline">Grafische Ansicht</span>
          </Button>
          <Button
            variant={viewMode === "table" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("table")}
            className="flex items-center gap-2"
          >
            <List className="h-4 w-4" />
            <span className="hidden sm:inline">Tabellarische Ansicht</span>
          </Button>
        </div>
      </div>

      <div className="border rounded-md" style={{ height: isTablet ? "60vh" : "70vh" }}>
        {viewMode === "graph" ? (
          <>
            <div className="absolute z-10 top-4 right-4 flex gap-2">
              <Button size="icon" variant="outline" onClick={handleZoomIn} aria-label="Zoom in">
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button size="icon" variant="outline" onClick={handleZoomOut} aria-label="Zoom out">
                <ZoomOut className="h-4 w-4" />
              </Button>
            </div>

            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              nodeTypes={nodeTypes}
              fitView
              minZoom={0.5}
              maxZoom={2}
              proOptions={{ hideAttribution: true }}
            >
              <Background />
              <Controls position="bottom-right" />

              {/* Panel for layout controls */}
              <Panel position="top-left" className="bg-background p-2 rounded-md shadow-sm border">
                <div className="flex flex-col gap-2">
                  <div className="h-px bg-border my-2" />

                  <Button size="sm" onClick={() => onLayout("TB")} className="flex items-center gap-2">
                    <LayoutGrid className="h-4 w-4" />
                    <span className="hidden sm:inline">Vertikales Layout</span>
                  </Button>
                  <Button size="sm" onClick={() => onLayout("LR")} className="flex items-center gap-2">
                    <LayoutGrid className="h-4 w-4 rotate-90" />
                    <span className="hidden sm:inline">Horizontales Layout</span>
                  </Button>
                </div>
              </Panel>
            </ReactFlow>
          </>
        ) : (
          <div className="p-4 h-full overflow-auto">
            <DocumentFlowTable
              initialDocumentId={selectedDocumentId || undefined}
              onViewDocument={handleDocumentChange}
            />
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * DocumentFlow component that displays a visual representation of document relationships
 * Wrapped with ReactFlowProvider to provide the required context
 */
export function DocumentFlow({ initialDocumentId }: DocumentFlowProps) {
  return (
    <ReactFlowProvider>
      <DocumentFlowInner initialDocumentId={initialDocumentId} />
    </ReactFlowProvider>
  )
}

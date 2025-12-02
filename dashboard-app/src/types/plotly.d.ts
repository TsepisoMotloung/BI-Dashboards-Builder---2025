declare module 'plotly.js-dist-min' {
  const Plotly: any
  export default Plotly
}

declare module 'react-plotly.js' {
  import { ReactNode } from 'react'
  interface PlotlyComponentProps {
    data: any[]
    layout?: any
    config?: any
    useResizeHandler?: boolean
  }
  const PlotlyComponent: React.ComponentType<PlotlyComponentProps>
  export default PlotlyComponent
}

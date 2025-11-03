# Visualization Guide

## ✅ Chart Components Available

The dashboard now includes fully functional Plotly.js chart components!

### Available Charts

1. **BarChart** - Bar/column charts with grouping and stacking
2. **LineChart** - Line charts with markers
3. **PieChart** - Pie charts with percentages
4. **ScatterChart** - Scatter plots for correlation analysis
5. **ChartWrapper** - Base wrapper for custom Plotly charts

## 📊 Using Chart Components

### Bar Chart

```tsx
import { BarChart } from "@/components/charts/BarChart"

<BarChart
  data={[
    {
      x: ["Jan", "Feb", "Mar", "Apr"],
      y: [20, 35, 30, 45],
      name: "Sales",
      color: "#3B82F6"
    }
  ]}
  title="Monthly Sales"
  xAxisTitle="Month"
  yAxisTitle="Amount ($)"
  height={400}
/>
```

### Line Chart

```tsx
import { LineChart } from "@/components/charts/LineChart"

<LineChart
  data={[
    {
      x: ["Jan", "Feb", "Mar", "Apr"],
      y: [100, 150, 130, 180],
      name: "Revenue",
      color: "#10B981",
      mode: "lines+markers"
    }
  ]}
  title="Revenue Trend"
  xAxisTitle="Month"
  yAxisTitle="Revenue ($)"
  height={400}
/>
```

### Pie Chart

```tsx
import { PieChart } from "@/components/charts/PieChart"

<PieChart
  data={{
    labels: ["Product A", "Product B", "Product C"],
    values: [40, 35, 25],
    colors: ["#3B82F6", "#10B981", "#F59E0B"]
  }}
  title="Sales by Product"
  height={400}
  showLegend={true}
/>
```

### Scatter Chart

```tsx
import { ScatterChart } from "@/components/charts/ScatterChart"

<ScatterChart
  data={[
    {
      x: [1, 2, 3, 4, 5],
      y: [10, 15, 13, 17, 20],
      name: "Dataset 1",
      color: "#8B5CF6"
    }
  ]}
  title="Correlation Analysis"
  xAxisTitle="Variable X"
  yAxisTitle="Variable Y"
  height={400}
/>
```

## 🎨 Chart Styling

All charts use consistent styling:
- **Font**: Inter (system font)
- **Colors**: Tailwind CSS color palette
- **Grid**: Light gray (#E5E7EB)
- **Background**: White
- **Margins**: Optimized for readability

### Custom Colors

```tsx
const colors = [
  "#3B82F6", // Blue
  "#10B981", // Green
  "#F59E0B", // Orange
  "#EF4444", // Red
  "#8B5CF6", // Purple
  "#EC4899", // Pink
  "#06B6D4", // Cyan
]
```

## 📈 Dashboard Viewer

### Features

✅ Display multiple charts in grid layout
✅ Tab navigation for organized dashboards
✅ Responsive design (mobile-friendly)
✅ Sample data for demonstration
✅ Export to PDF (button ready)
✅ Refresh data (button ready)

### Pages Created

1. `/dashboard/my-dashboards` - List all dashboards
2. `/dashboard/my-dashboards/[id]` - View specific dashboard

## 🔧 Seeding Sample Dashboards

To create sample dashboards with visualizations:

```bash
npm run seed
```

This creates:
- **Sales Analytics Dashboard** with 3 visualizations
- **Customer Insights Dashboard** with 2 visualizations

## 📊 Dashboard Structure

Each dashboard contains:
- **Metadata**: Name, description, creator
- **Tabs**: Multiple tabs for organization
- **Visualizations**: Charts within each tab

### Database Schema

```
Dashboard
  ├── DashboardTab[]
  │     └── Visualization[]
  └── DashboardPermission[]
```

### Visualization Config

Stored as JSON in database:

```json
{
  "title": "Monthly Sales",
  "xAxisTitle": "Month",
  "yAxisTitle": "Sales ($)",
  "chartType": "bar",
  "colors": ["#3B82F6"]
}
```

## 🔌 Data Integration

Currently using sample data. To connect real data:

### Option 1: Direct Database Query

```tsx
// In server component
const data = await prisma.$queryRaw`
  SELECT month, SUM(amount) as total 
  FROM sales 
  GROUP BY month
`

// Transform for chart
const chartData = {
  x: data.map(d => d.month),
  y: data.map(d => Number(d.total))
}
```

### Option 2: ETL API

```tsx
// Using API helper
import { etlApi } from "@/lib/api"

const data = await etlApi.getDataModels()
```

### Option 3: Dynamic Tables

Query from dynamically created tables:

```tsx
const tableName = `data_${modelName.toLowerCase()}`
const data = await prisma.$queryRawUnsafe(
  `SELECT * FROM ${tableName} LIMIT 100`
)
```

## 🎯 Interactive Features

### Planned Features (Future)

- ⏳ Drill-down (click chart to see details)
- ⏳ Filters (date range, categories)
- ⏳ Real-time updates
- ⏳ Chart customization UI
- ⏳ Dashboard builder

## 📱 Responsive Design

Charts automatically resize on:
- Desktop (full width)
- Tablet (2 columns)
- Mobile (1 column)

## 🔍 Testing Charts

### Test 1: View Sample Dashboard

1. Run seed script: `npm run seed`
2. Navigate to "My Dashboards"
3. Click "Sales Analytics Dashboard"
4. See bar, line, and pie charts

### Test 2: Create Custom Visualization

In dashboard viewer, charts render from database config.

### Test 3: Export (Ready)

Export button is ready - will integrate jsPDF in next chunk.

## 🎨 Chart Examples

### Multiple Series Bar Chart

```tsx
<BarChart
  data={[
    {
      x: ["Q1", "Q2", "Q3", "Q4"],
      y: [100, 120, 130, 150],
      name: "2023",
      color: "#3B82F6"
    },
    {
      x: ["Q1", "Q2", "Q3", "Q4"],
      y: [110, 125, 140, 160],
      name: "2024",
      color: "#10B981"
    }
  ]}
  title="Quarterly Comparison"
  stacked={false}
/>
```

### Horizontal Bar Chart

```tsx
<BarChart
  data={[...]}
  horizontal={true}
  title="Top Products"
/>
```

### Time Series Line Chart

```tsx
<LineChart
  data={[
    {
      x: dates, // Array of Date objects
      y: values,
      name: "Daily Sales",
      mode: "lines"
    }
  ]}
  title="Sales Over Time"
/>
```

## 🚀 Performance

Charts are optimized:
- ✅ Client-side rendering (no SSR overhead)
- ✅ Lazy loading with dynamic imports
- ✅ Memoization for data processing
- ✅ Efficient Plotly.js bundle

## 🔒 Security

- ✅ All data queries server-side
- ✅ User permissions checked
- ✅ No client-side SQL
- ✅ XSS protection via React

## 📚 Resources

- [Plotly.js Documentation](https://plotly.com/javascript/)
- [Chart Types](https://plotly.com/javascript/basic-charts/)
- [Layout Options](https://plotly.com/javascript/reference/layout/)

## ✅ Verification

Working features:
- ✅ Chart components render correctly
- ✅ Sample data displays in charts
- ✅ Dashboard viewer functional
- ✅ Responsive layouts work
- ✅ Navigation between dashboards
- ✅ Multiple chart types supported

## 🔜 Next Steps

Will add in final chunk:
1. PDF export functionality
2. Dashboard builder UI
3. Chart customization
4. Real data integration
5. Filters and interactions

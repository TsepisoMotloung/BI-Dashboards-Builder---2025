import { PrismaClient, UserStatus } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('Seeding sample dashboard...')

  // Find or create admin user
  const admin = await prisma.user.findFirst({
    where: {
      email: 'admin@example.com',
      // UserStatus: 'active',
    },
  })

  if (!admin) {
    console.error('Admin user not found. Please run ETL app init_db.py first.')
    return
  }

  // Create sample dashboard
  const dashboard = await prisma.dashboard.create({
    data: {
      name: 'Sales Analytics Dashboard',
      description: 'Overview of sales performance and trends',
      created_by: admin.id,
      tabs: {
        create: [
          {
            name: 'Overview',
            order: 0,
            visualizations: {
              create: [
                {
                  type: 'bar',
                  order: 0,
                  config: JSON.stringify({
                    title: 'Monthly Sales',
                    xAxisTitle: 'Month',
                    yAxisTitle: 'Sales ($)',
                  }),
                  query: 'SELECT month, SUM(amount) as total FROM sales GROUP BY month',
                },
                {
                  type: 'line',
                  order: 1,
                  config: JSON.stringify({
                    title: 'Revenue Trend',
                    xAxisTitle: 'Date',
                    yAxisTitle: 'Revenue ($)',
                  }),
                  query: 'SELECT date, revenue FROM daily_revenue ORDER BY date',
                },
                {
                  type: 'pie',
                  order: 2,
                  config: JSON.stringify({
                    title: 'Sales by Category',
                  }),
                  query: 'SELECT category, SUM(amount) as total FROM sales GROUP BY category',
                },
              ],
            },
          },
          {
            name: 'Details',
            order: 1,
            visualizations: {
              create: [
                {
                  type: 'bar',
                  order: 0,
                  config: JSON.stringify({
                    title: 'Top Products',
                    xAxisTitle: 'Product',
                    yAxisTitle: 'Units Sold',
                  }),
                  query: 'SELECT product_name, COUNT(*) as units FROM sales GROUP BY product_name ORDER BY units DESC LIMIT 10',
                },
              ],
            },
          },
        ],
      },
    },
  })

  console.log(`✅ Created dashboard: ${dashboard.name} (ID: ${dashboard.id})`)
  
  // Create another sample dashboard
  const dashboard2 = await prisma.dashboard.create({
    data: {
      name: 'Customer Insights',
      description: 'Customer behavior and demographics analysis',
      created_by: admin.id,
      tabs: {
        create: [
          {
            name: 'Demographics',
            order: 0,
            visualizations: {
              create: [
                {
                  type: 'pie',
                  order: 0,
                  config: JSON.stringify({
                    title: 'Customers by Region',
                  }),
                  query: 'SELECT region, COUNT(*) as count FROM customers GROUP BY region',
                },
                {
                  type: 'bar',
                  order: 1,
                  config: JSON.stringify({
                    title: 'Age Distribution',
                    xAxisTitle: 'Age Group',
                    yAxisTitle: 'Count',
                  }),
                  query: 'SELECT age_group, COUNT(*) as count FROM customers GROUP BY age_group',
                },
              ],
            },
          },
        ],
      },
    },
  })

  console.log(`✅ Created dashboard: ${dashboard2.name} (ID: ${dashboard2.id})`)
  console.log('\n✅ Sample dashboards created successfully!')
}

main()
  .catch((e) => {
    console.error('Error seeding dashboard:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })

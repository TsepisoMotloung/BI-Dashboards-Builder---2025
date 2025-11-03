/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config) => {
    config.externals.push({
      'argon2': 'commonjs argon2',
    })
    return config
  },
}

export default nextConfig

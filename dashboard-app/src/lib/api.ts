const ETL_API_URL = process.env.ETL_API_URL || "http://localhost:8000/api/v1"

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = "ApiError"
  }
}

async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const url = `${ETL_API_URL}${endpoint}`

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }))
    throw new ApiError(response.status, error.detail || "Request failed")
  }

  return response.json()
}

export const etlApi = {
  // Data Models
  async getDataModels() {
    return fetchApi("/data-models")
  },

  async getDataModel(id: number) {
    return fetchApi(`/data-models/${id}`)
  },

  async createDataModel(data: any) {
    return fetchApi("/data-models", {
      method: "POST",
      body: JSON.stringify(data),
    })
  },

  // Uploads
  async previewUpload(file: File) {
    const formData = new FormData()
    formData.append("file", file)

    return fetch(`${ETL_API_URL}/uploads/preview`, {
      method: "POST",
      body: formData,
    }).then((res) => res.json())
  },

  async uploadData(file: File, uploadRequest: any) {
    const formData = new FormData()
    formData.append("file", file)
    formData.append("upload_request", JSON.stringify(uploadRequest))

    return fetch(`${ETL_API_URL}/uploads`, {
      method: "POST",
      body: formData,
    }).then((res) => res.json())
  },

  async getUploads(params?: { model_id?: number; skip?: number; limit?: number }) {
    const query = new URLSearchParams()
    if (params?.model_id) query.append("model_id", params.model_id.toString())
    if (params?.skip) query.append("skip", params.skip.toString())
    if (params?.limit) query.append("limit", params.limit.toString())

    return fetchApi(`/uploads?${query}`)
  },

  // Authentication
  async login(email: string, password: string) {
    return fetchApi("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })
  },

  async register(email: string, password: string, full_name: string) {
    return fetchApi("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    })
  },
}

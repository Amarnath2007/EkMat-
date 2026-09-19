const BASE_URL = import.meta.env.VITE_API_URL || '';

export async function fetchJson(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const defaultHeaders = {
    'Accept': 'application/json',
  };

  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  const response = await fetch(url, config);
  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch (e) {
      errorDetail = response.statusText;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

// Analytics & Summary
export const getAnalyticsSummary = () => fetchJson('/api/analytics/summary');

// Materials
export const listMaterials = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return fetchJson(`/api/materials?${query}`);
};

export const getMaterial = (id) => fetchJson(`/api/materials/${id}`);

export const importMaterialsCSV = (formData) => {
  return fetchJson('/api/materials/import', {
    method: 'POST',
    body: formData,
  });
};

export const runMatching = () => {
  return fetchJson('/api/materials/run-matching', {
    method: 'POST',
  });
};

// Matches
export const listMatches = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return fetchJson(`/api/matches?${query}`);
};

export const getMatch = (id) => fetchJson(`/api/matches/${id}`);

export const approveMatch = (id, reviewedBy = 'Govt Evaluator') => {
  return fetchJson(`/api/matches/${id}/approve`, {
    method: 'POST',
    body: JSON.stringify({ reviewed_by: reviewedBy }),
  });
};

export const editApproveMatch = (id, data) => {
  return fetchJson(`/api/matches/${id}/edit-approve`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
};

export const rejectMatch = (id, reviewedBy = 'Govt Evaluator', reason = 'Technical specification divergence') => {
  return fetchJson(`/api/matches/${id}/reject`, {
    method: 'POST',
    body: JSON.stringify({ reviewed_by: reviewedBy, rejection_reason: reason }),
  });
};

// Common Materials
export const listCommonMaterials = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return fetchJson(`/api/common-materials?${query}`);
};

export const getCommonMaterial = (id) => fetchJson(`/api/common-materials/${id}`);

// Audit Log
export const getAuditTrail = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return fetchJson(`/api/audit-log?${query}`);
};

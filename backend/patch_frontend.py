import os

filepath = r'c:\BotRedaman\frontend\src\App.tsx'

with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update fetchOnuHistory definition
old_fetch_def = """  const fetchOnuHistory = async (onuId: string) => {
    setLoadingHistory(true);
    try {
      const res = await axios.get(`${API_BASE}/chart_data?onu_id=${onuId}`);"""

new_fetch_def = """  const fetchOnuHistory = async (onuId: string, oltId?: string | number) => {
    setLoadingHistory(true);
    try {
      let url = `${API_BASE}/chart_data?onu_id=${onuId}`;
      if (oltId) url += `&olt_id=${oltId}`;
      const res = await axios.get(url);"""

code = code.replace(old_fetch_def, new_fetch_def)

# 2. Update fetchOnuHistory calls
code = code.replace("fetchOnuHistory(selectedOnu.onu_id);", "fetchOnuHistory(selectedOnu.onu_id, selectedOnu.olt_id);")

# 3. Update the Deep Link loading logic
old_deep_link = """      // Check if there is a deep link for a specific ONU ID
      const params = new URLSearchParams(window.location.search);
      const onuIdParam = params.get('onu_id');
      if (onuIdParam) {
        const found = resAtt.data.find((a: any) => a.onu_id === onuIdParam);
        if (found) {
          setSelectedOnu(found);
        }
      }"""

new_deep_link = """      // Check if there is a deep link for a specific ONU ID
      const params = new URLSearchParams(window.location.search);
      const onuIdParam = params.get('onu_id');
      const oltIdParam = params.get('olt_id');
      if (onuIdParam) {
        let found;
        if (oltIdParam) {
            found = resAtt.data.find((a: any) => String(a.onu_id) === String(onuIdParam) && String(a.olt_id) === String(oltIdParam));
        } else {
            found = resAtt.data.find((a: any) => String(a.onu_id) === String(onuIdParam));
        }
        if (found) {
          setSelectedOnu(found);
        }
      }"""

code = code.replace(old_deep_link, new_deep_link)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)

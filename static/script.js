document.addEventListener('DOMContentLoaded', () => {
    const dataBody = document.getElementById('data-body');
    const refreshBtn = document.getElementById('refresh-btn');
    const searchInput = document.getElementById('search-input');
    const totalOltEl = document.getElementById('total-olt');
    const criticalCountEl = document.getElementById('critical-count');

    let allData = []; // Menyimpan semua data agar bisa difilter di lokal

    const formatDate = (dateString) => {
        const d = new Date(dateString);
        return d.toLocaleTimeString('id-ID', { hour: '2-digit', minute:'2-digit', second:'2-digit' });
    };

    const getStatusBadge = (rxPower) => {
        if (rxPower === null || rxPower === undefined) return '<span class="badge">N/A</span>';
        if (rxPower > -24) return '<span class="badge good">Good</span>';
        if (rxPower >= -27) return '<span class="badge warning">Warning</span>';
        return '<span class="badge critical">Critical</span>';
    };

    const renderTable = (dataToRender) => {
        let html = '';
        let criticalCount = 0;

        if(dataToRender.length === 0) {
            html = `<tr><td colspan="8" style="text-align:center; padding: 2rem;">Tidak ada data ditemukan.</td></tr>`;
        } else {
            dataToRender.forEach(item => {
                if(item.rx_power < -27) criticalCount++;
                
                const customerName = item.customer_name ? item.customer_name : "Tanpa Nama";
                
                html += `
                    <tr>
                        <td><strong>${item.olt_name}</strong></td>
                        <td>${item.port_name}</td>
                        <td>${item.onu_id}</td>
                        <td><strong>${customerName}</strong></td>
                        <td class="${item.rx_power < -27 ? 'danger-text' : (item.rx_power >= -24 ? 'success-text' : 'warning-text')}">
                            <strong>${item.rx_power !== null ? item.rx_power.toFixed(2) : '-'}</strong>
                        </td>
                        <td>${item.tx_power !== null ? item.tx_power.toFixed(2) : '-'}</td>
                        <td>${formatDate(item.timestamp)}</td>
                        <td>${getStatusBadge(item.rx_power)}</td>
                    </tr>
                `;
            });
        }
        dataBody.innerHTML = html;
        // Update critical count hanya berdasarkan semua data (bukan hasil search) 
        // tapi untuk kemudahan kita tampilkan yg terfilter
    };

    const fetchData = async () => {
        try {
            refreshBtn.textContent = 'Loading...';
            
            const oltRes = await fetch('/api/olts');
            const olts = await oltRes.json();
            totalOltEl.textContent = olts.length;

            const attenRes = await fetch('/api/attenuations');
            allData = await attenRes.json();
            
            // Hitung critical dari semua data
            const totalCritical = allData.filter(d => d.rx_power < -27).length;
            criticalCountEl.textContent = totalCritical;
            
            // Render ulang (pertahankan filter search jika ada)
            handleSearch();

            setTimeout(() => { refreshBtn.textContent = 'Refresh Data'; }, 500);

        } catch (error) {
            console.error('Gagal mengambil data:', error);
            refreshBtn.textContent = 'Error!';
            setTimeout(() => { refreshBtn.textContent = 'Refresh Data'; }, 2000);
        }
    };

    const handleSearch = () => {
        const query = searchInput.value.toLowerCase();
        if (query.trim() === '') {
            renderTable(allData);
        } else {
            const filtered = allData.filter(item => 
                (item.customer_name && item.customer_name.toLowerCase().includes(query)) ||
                (item.onu_id && item.onu_id.toLowerCase().includes(query)) ||
                (item.olt_name && item.olt_name.toLowerCase().includes(query))
            );
            renderTable(filtered);
        }
    };

    refreshBtn.addEventListener('click', fetchData);
    searchInput.addEventListener('input', handleSearch); // Live filtering!

    fetchData();
    setInterval(fetchData, 30000);
});

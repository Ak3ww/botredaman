# Perbaikan False Alarm "Back to Offline"

Terdapat bug di mana bot salah menafsirkan status ONU yang baru saja kembali normal menjadi OFFLINE lagi (terutama pada VSOL dan HSGQ).

## Penyebab Bug

1. **VSOL**: Bot sangat bergantung pada nilai `dbm` (RX Power). Jika SNMP mengalami UDP Packet Loss untuk sepersekian detik, `dbm` terbaca sebagai `None`. Logika lama langsung menetapkan `is_currently_offline = True` jika `dbm` None, tanpa melihat bahwa `last_up` > `last_down` (yang artinya ONU sebenarnya masih menyala).
2. **HSGQ**: Jika packet loss terjadi pada SNMP sehingga `status_val` gagal ditarik, bot jatuh ke logika `is_currently_offline = (dbm is None)`. Jika `dbm` juga gagal ditarik, maka bot mengira ONU tersebut OFFLINE.

## Proposed Changes

Kita akan merombak blok penentuan `is_currently_offline` di dalam `C:\BotRedaman\backend\collector.py` untuk menjadi lebih cerdas dan tahan banting (*fault-tolerant*).

### MODIFY `C:\BotRedaman\backend\collector.py`
Ubah logika pada baris 897 ke bawah menjadi:

```python
                # Tentukan online/offline status secara akurat (berdasarkan OLT)
                is_currently_offline = False
                
                # Fungsi helper untuk fallback ke status database lama jika data OLT kosong (Packet Loss)
                def get_previous_offline_state():
                    state_row = cursor.execute('SELECT status FROM alert_states WHERE onu_id = ? AND olt_id = ?', (onu_idx, olt_id)).fetchone()
                    return (state_row[0] == 'OFFLINE') if state_row else False

                if olt_brand == "GGCLINK":
                    status_val = status_data.get(onu_idx)
                    if status_val is not None:
                        is_currently_offline = (str(status_val).strip() != '1')
                    else:
                        is_currently_offline = get_previous_offline_state()

                elif olt_brand == "HSGQ":
                    status_val = status_data.get(onu_idx)
                    if status_val is not None:
                        is_currently_offline = (str(status_val).strip() != '1')
                    else:
                        if dbm is not None:
                            is_currently_offline = False
                        else:
                            is_currently_offline = get_previous_offline_state()
                    
                    if alive and alive != "0":
                        alive = format_hsgq_alive(alive)
                    else:
                        alive = "-"

                elif olt_brand == "VSOL":
                    valid_up = last_up and str(last_up) not in ("N/A", "0000-00-00 00:00:00", "")
                    valid_down = last_down and str(last_down) not in ("N/A", "0000-00-00 00:00:00", "")
                    
                    if valid_up and valid_down:
                        # Jika kedua timestamp valid, percayai timestamp OLT (Paling Akurat)
                        is_currently_offline = (str(last_down) > str(last_up))
                    else:
                        # Jika timestamp tidak lengkap, cek dbm
                        if dbm is not None:
                            is_currently_offline = False
                        else:
                            is_currently_offline = get_previous_offline_state()
```

## User Review Required

> [!WARNING]
> Logika ini akan mengabaikan nilai RX Power (`dbm = None`) jika OLT secara eksplisit masih menyatakan bahwa `last_up` > `last_down` (di VSOL) atau `status = 1` (di HSGQ). Ini sangat ampuh untuk mencegah *False Alarm* akibat *SNMP Timeout* sesaat. Apakah Bapak setuju dengan logika *Hysteresis* (mengingat status lama) ini?

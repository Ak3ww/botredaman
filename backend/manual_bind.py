import sqlite3

raw_data = """
1	16777475	HANAN	hanan EMGANS (FREE FAMILY)
1	16777484	ADAM DHARMAWAN	adam_dharmawan EMGADAM (FREE ADAM)
1	16777486	ONT01/014	ont01014 (BELUM TERSETUP)
1	16777489	ANNISA SYAFIRA	annisa_syafira  EMG038 (ANISSA SHAFIRA)
1	16777490	MUHAMMAD AGUNG SETIAWAN	muhammad_agung_setiawan EMG030 (MUHAMMAD AGUNG)
1	16777492	POS DEPAN 2	pos_depan_2 FREE POS RT 8 RW 14 FAS007
1	16777498	ONT01/026	ont01026
1	16777501	ONT01/029	ont01029
1	16777515	HANIDA FAUZIAH	hanida_fauziah HANIDAH FAUZIAH EMG155
1	16777517	FAIZ ARIFANDY	faiz_arifandy FAIZ ARIFANDY EMG074
1	16777519	M. CERRY RIANDI	m_cerry_riandi M. CERRI RIANDI EMG037
1	16777528	REZA VIRDIANSYAH	reza_virdiansyah  REZA VARDIANSYAH EMG211
1	16777529	CHESTARIANI TRI WAHYUNI	chestariani_tri_wahyuni Pelanggan: CHESTARIANI AYU TRIWAHYUNI EMG025
1	16777534	ERRITETI SITOMPUL	erriteti_sitompul Pelanggan: ERRITETTI SITOMPUL EMG127
1	16777537	GERIL VALDO	geril_valdo EMG151
1	16777547	BUKHORI BOLANG	bukhori_bolang EMG147
1	16777548	TITO SHADAM	tito_shadam EMG154
1	16777556	KANTOR EUGINE	kantor_eugine EMGCC1
1	16777560	UNTUNG PRIYANTO	untung_priyanto EMG235
1	16777565	BETTY RIAMA SIMATUPANG	betty_riama_simatupang EMG179
1	16777571	ESKA PERDANA	eska_perdana EMG214 
1	16777732	ALIF DAFA ALRAFI	alif_dafa_alrafi EMG197
1	16777736	OKTAFIA SYAFIATUN	oktafia_syafiatun EMG287
1	16777738	AGUS	774118 EMG237
1	16777739	PUTRI INDAH	putri_indah EMG120
1	16777744	RISKA	352893 EMG 232
1	16777751	SALBIYAH	salbiyah EMG285
1	16777809	SURYANIH	suryanih EMG262
1	16777822	RINI SUGIATI	rini_sugiati EMG066
1	16777826	ARI AKBAR PRATAMA	ari_akbar_pratama EMG185
1	16777830	DERIE WIBOWO	derie_wibowo  EMG218 
1	16777833	M. REZA SUHADA	m_reza_suhada EMG225
1	16777834	R. MUHAMMAD IMRAN	r_muhammad_imran EMG233
1	16777838	DWI SUNARDI SETIABUDI	dwi_sunardi_setiabudi EMG238
1	16777840	NINA FEBRIYANTI	nina_febriyanti EMG063
1	16777841	RAMLAH NASUTION	ramlah_nasution EMG249
1	16777843	AHMAD IBRAHIM	ahmad_ibrahim EMG077
1	16777845	SALSABILA	salsabila EMG228
1	16777848	MUHAMMAD	312367 EMG230
1	16777851	NIMAS FADILLAH	nimas_fadillah EMG221
2	1.18	M-RAFLY	mrafly EMG002
2	1.24	ARIESTA-MIRANDA	ariestamiranda EMG005
2	1.33	M-AKMAL-FALIH	makmalfalih EMG231
2	1.38	LUKMAN-NULHAKIM	lukmannulhakim EMG160
2	1.39	DADANG	dadang EMG158
2	1.48	GILANG-SAHPTURA	gilangsahptura EMG204
2	1.54	DINA-GIANTIKA	dinagiantika EMG009
2	1.55	FREE-AMAE	freeamae EMGAMAI
2	1.69	DEDI-TJAHJONO	deditjahjono EMG017
2	1.7	REYHAN-SEP-DWI-P	reyhansepdwip EMG146
3	101002	DENDRA NARSHAFTIAWAN	dendra_narshaftiawan EMG152
3	101016	NURIYANTI TARIGAN	nuriyanti_tarigan EMG113
3	101023	ANDIKA PUTRA NUGRAHA	andika_putra_nugraha EMG094
3	101028	FARSA JUSTI	farsa_justi EMG178
3	101041	TRIYATNI MUSTIKA	triyatni_mustika EMG124
3	101044	FREE APUD	free_apud FAS010
3	101045	POSYANDU RW 16	posyandu_rw_16 FAS027
3	101052	PARYONO DK	paryono_dk  EMG250
3	101054	SRI WULANTO	sri_wulanto EMG252
3	101055	EDY SUMARDI	edy_sumardi EMG254
3	101056	PARYONO RT05	paryono_rt05 EMG086
3	102005	ONU-1/2:5	onu125
3	102013	TIRTO APRIYANTO	tirto_apriyanto EMG044
3	102014	TOMMY FARDIANSYAH	tommy_fardiansyah  EMG203
3	102022	ADANG EFENDI	adang_efendi EMG192
3	102027	IVA EMILIA	iva_emilia EMGIVA
3	102029	RT 05 RW 14	rt_05_rw_14 FAS019
3	102030	WAHID MAHFUZI	wahid_mahfuzi EMG201
3	102034	RT 3 RW 14	rt_3_rw_14 FAS017
3	102035	ALI SANDY	ali_sandy EMG195
3	102038	POS RW 14	pos_rw_14 FAS015 
3	102039	GANDA PRAYONO	ganda_prayono EMG244 
3	102040	EBEN MARTHIN	eben_marthin EMG236
4	101004	AGUS PRASETYO	agus_prasetyo EMG143
4	101005	RANI ANDRIYANI	rani_andriyani EMG183
4	101007	SANSAN ABDUL FATA	sansan_abdul_fata EMG274
4	101011	ERNA RUSDIANA	erna_rusdiana EMG281
4	101012	MEIKA HERMANI	meika_hermani EMG121
"""

# Parsing logic:
# We need to extract the actual PPPoE binding, which is usually EMGxxx or FASxxx or EMGAMAI or EMGCC1
import re

updates = []
for line in raw_data.strip().split('\n'):
    parts = line.split('\t')
    if len(parts) >= 4:
        olt_id = parts[0].strip()
        onu_id = parts[1].strip()
        
        # In some rows with numbers in the name (e.g. AGUS \t 774118), it got split into 5 parts
        # Let's just find EMG... or FAS... in the whole line string
        
        match = re.search(r'(EMG[A-Z0-9]+|FAS[A-Z0-9]+)', line)
        if match:
            pppoe_user = match.group(1)
            updates.append((pppoe_user, olt_id, onu_id))

conn = sqlite3.connect(r'C:\BotRedaman\backend\redaman.db')
c = conn.cursor()

print(f"Updating {len(updates)} records...")
count = 0
for pppoe_user, olt_id, onu_id in updates:
    # Update to the database
    c.execute('UPDATE onu_name_cache SET pppoe_username = ? WHERE olt_id = ? AND onu_id = ?', (pppoe_user, olt_id, onu_id))
    if c.rowcount > 0:
        count += 1
        print(f"[{olt_id} - {onu_id}] Bound to {pppoe_user}")
    else:
        print(f"[{olt_id} - {onu_id}] WARNING: Record not found in DB!")

conn.commit()
conn.close()
print(f"\nSuccessfully bound {count} ONUs manually.")

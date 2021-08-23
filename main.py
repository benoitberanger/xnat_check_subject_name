import psycopg2 # PostGreSQL lib
import re       # regular expression
from datetime import date
import csv
import os       # join path and write in file
import json

# Load credentials
cred_path = os.path.join(os.path.expanduser("~"),"credentials_xnat_read_only")
fid = open(cred_path)
cred_dic = json.load(fid)
fid.close()

# Connect to DB
con = psycopg2.connect(database='xnat_prod', user=cred_dic['user'], password=cred_dic['password'], host="192.168.80.111", port="5432")
print("Database connected successfully")
cur = con.cursor()
print("Database opened successfully")

# Get all protocol
#cur.execute("SELECT * FROM xnat_projectdata;")
#table_protocol = cur.fetchall()

now = date.today().strftime('%Y_%m_%d')

regex_verio = {
    'ALITHIOS_COMB157G2399'     : r'COMB157G2399_2037_[0-9]{7}_w[0-9]+',
    # 'ARISE_ALTHEA'              : r'ARISE_161[0-9]{2}_(Week[0-9]+|Early_Termination)',
    'ASSESS'                    : r'ASSESS_[A-Z]{2,3}_[0-9]{3}',
    'BIOMRI_CADA'               : r'BIOMRI_CADA_001_[0-9]{3}_[A-Z]{2}',
    'CATMAP'                    : r'CATMAP_S[0-9]{2}',
    'CONTROLFOOD'               : r'CONTROLFOOD_[0-9]{3}_[A-Z]{2}_[0-9]{8}',
    'D_LAY'                     : r'D_LAY_C35_P[0-9]{3}_(M[0-9]+|Baseline|Unscheduled)',
    'EMBARK'                    : r'221AD304_251_[0-9]{3}_(w[0-9]+|Screening|Unscheduled|EOT)',
    'EMBARK_249'                : r'221AD304_249_[0-9]{3}_(w[0-9]+|Screening|Unscheduled|EOT)',
    'EXPAND'                    : r'EXPAND_3007(_[A-Z]{2})?_[0-9]{3}_(Baseline|M12|EOS|EOT|M24|M60E|Ext)',
    'GN40040_LAURIET'           : r'GN40040_543[0-9]{3}_(w[0-9]+|Screening|Unscheduled|ET)',
    # 'TAURIEL_GN39763_GENENTECH' : r'GN39763_305525_268[0-9]{3}_(Week[0-9]+|Screening)',
    'HEMIANOTACS'               : r'HEMIANOTACS_(P|T)[0-9]{3}',
    'ICE_EMDR'                  : r'ICE_EMDR_[A-Z]{4}_[0-9]{2}_V[0-9]+',
    'LEOPOLD'                   : r'LEOPOLD_(001|002)_[0-9]{4}_[A-Z]{2}_(M0|M36)',
    'METIS'                     : r'METIS_151229_1513_[0-9]{3}_(Week[0-9]+|Baseline|NewBaseline|Unscheduled|UnscheduledRadiationNecrosis|SRS)',
    'PASADENA'                  : r'BP39529_302121_[0-9]{5}_(Screening|W[0-9]+)',
    'PASADENA_BP39529'          : r'BP39529_302121_10367_Week104',
    'PASADENA_BP39529_P3'       : r'BP39529_302121_DummyRun',
    'PERSEUS'                   : r'EFC16035_2500014_250001435[0-9]{3}_(Screening|m[0-9]+|EOT|EOS)',
    'PERSPECTIVE'               : r'PERSPECTIVE_7501_[0-9]{3}_(V[0-9]+|EOT)',
    'PREDEMPARK'                : r'PREDEMPARK_(002|003)_[0-9]{4}_[A-Z]{2}',
    'PREDICT_PGRN'              : r'PREDICT_PGRN_SAL_[0-9]{2}_[A-Z]{2}_(M[0-9]+)',
    'QUIT_COC'                  : r'QUIT_COC_[0-9]{2}_[0-9]{2}_[A-Z]{2}(_V2)?',
    'SOM_ALS2'                  : r'SOM_ALS2_[A-Z]{2}_[0-9]{2}_(P|T)',
    'STOP_I_SEP'                : r'STOP_I_SEP_04_[0-9]{3}_(M[0-9]+|Rechute)',
    'TANGO_251AD201'            : r'251AD201_252[0-9]{3}_(w[0-9]+|Screening|Unscheduled|ET)',
    'TERIS'                     : r'TERIS_09_[0-9]{2}_(Baseline|Week48|Week96|EOT)',
    'TMS_CCS'                   : r'TMS_CCS_[A-Z]{4}_(1|2)',
    'WPMEG'                     : r'WPMEG_S[0-9]{2}',
}

regex_prisma = {
    'ACUITY'                : r'ACUITY_[0-9]{2}',
    'ADOLIMIS'              : r'ADOLIMIS_[A-Z]{2,}_(P|T)_[0-9]{2}',
    # 'AGENT_10'              : r'AGENT10_[0-9]{3}',
    # 'AMEDYST'               : r'AMEDYST_C16_128_01_[A-Z]{2}_[0-9]{3}(_V[0-9])?',
    'ARTCONNECT'            : r'ART_CONNECT_001_[0-9]{4}_[A-Z]{2}_V[0-9]+',
    'ASPIRE_MSA'            : r'ASPIRE_MSA_07_[0-9]{3}_[A-Z]{2}',
    'ATTACK'                : r'ATTACK_(P[0-9]{2}|T[0-9]{3}_[A-Z]{2})',
    'BAN_2401_Eisai'        : r'BAN2401_G000_301_[0-9]{8}_(Screening|Week9|Week13|Week27|Week53|Week79|Early_Termination|Unscheduled[0-9])',
    'CADET'                 : r'CADETS_(T|P)[0-9]{3}(_T18)?',
    'CADETS'                : r'CADETS_(T|P)[0-9]{3}(_T18)?',
    'CERMOI'                : r'CERMOI_ICM_[0-9]{3}_[A-Z]{2}_V[0-9]',
    'CLARIFY'               : r'CLARIFY_213[0-9]{4}',
    'CREAM_HD'              : r'CREAM_HD_11_[0-9]{2}_[A-Z]{2}',
    'ECOCAPTURE'            : r'ECOCAPTURE_(DFT|VS|DEP)_[A-Z]{2}_[0-9]{3}_[0-9]{2}_[0-9]{2}_[0-9]{4}',
    'ENERGYSEP'             : r'ENERGYSEP_(C|P)_[0-9]{2}_[A-Z]{2}_V(1|2|3)',
    'FLUMASEPT'             : r'FLUMASEPT_(P|C)_[0-9]{2}_[A-Z]{2}_V[0-9]+',
    'GENERATION_HD1'        : r'BN40423_317532_[0-9]{3}_(Month|Week)[0-9]+',
    'HAIS'                  : r'(HAIS(_CC)?_[0-9]{4}|DEEPTIME_S[0-9]{2}_(1|2))',
    'HORIZON'               : r'HORIZON_262SP101_201_[0-9]{3}_(Screening|Day[0-9]+)',
    'ICEBERG'               : r'ICEBERG_[A-Z]{2}_[0-9]{3}_V[0-9](_M)?',
    'IMAGLUT'               : r'IMAGLUT_[0-9]{3}_[0-9]{3}_[A-Z]{2}_V[0-9]',
    'INSIGHTEC'             : r'(ULTRABRAIN_001_[0-9]{3}_[A-Z]{2}_(V1_(INCLUSION|SPECTRO)|V(3|4|5|7)_CONTROL|V5_SPECTRO|V2_TTT)|DEV_[0-9]{3}_INSIGHTEC|INSIGHTEC_CRANE_[0-9]{3}|DQA|dqa)',
    'LEOPOLD_SHIVA'         : r'LEOPOLD_SHIVA_(001|002)_[0-9]{4}_[A-Z]{2}_(M0|M36)',
    'MAGIC'                 : r'MAGIC_(01|02)_[0-9]{3}_[A-Z]{2}',
    'MINO_AMN'              : r'(DEV_[0-9]+_MINO_AMN_C[0-9]{3})|(1020_102[0-9]{3})',
    'MOTI_STROKE'           : r'MOTI_STROKE_[A-Z]{2}[0-9]{2}',
    'NANORAD2'              : r'NANORAD2_03_[0-9]{3}_(Baseline|S[0-9]|M[0-9]|Post_IV)',
    'ON_STIM'               : r'ON_STIM_(P|VS)_[0-9]{2}_[A-Z]{2}',
    'OPTIDBS'               : r'OPTIDBS(_VS)?_[A-Z]{2,4}_[0-9]{2}',
    'PARKGAMEII'            : r'PARKGAMEII_[0-9]{3}_[A-Z]{2}_[0-9]{2}_[0-9]{2}_[0-9]{4}_V[0-9]',
    'POPB'                  : r'DEV_[0-9]{3}_POPB_SUJET[0-9]{2}',
    # 'WVE_HDSNP1_001'        : r'WVE_HDSNP1_001_3303_10[0-9]{2}_(Screening|V[0-9]|w[0-9]+|wET)',
    # 'WVE_HDSNP2_001'        : r'WVE_HDSNP2_001_3303_10[0-9]{2}_(Screening|V[0-9]|w[0-9]+|wET)',
    # 'WVE_HDSNP1_002'        : r'WVE_HDSNP1_002_3303_10[0-9]{2}_(Screening|V[0-9]|w[0-9]+|wET)',
    'PULSE'                 : r'PULSE_03_[0-9]{3}_[A-Z]{2}_(C|M)',
    'READISCA'              : r'(READISCA_PS_01_[0-9]{3}(_(6|12|24|36|48)mo)?|QA_PS)',
    'RESPIMUS'              : r'RESPIMUS_[A-Z]{2}_[0-9]{3}',
    'RETIMUS'               : r'RETIMUS_[A-Z]{2}_[0-9]{2}',
    'SCHIRANG'              : r'SCHIRANG_Patient[0-9]{3}(_V2)?',
    'SEP_BIO_PROGRESS'      : r'SEP_BP_[A-Z]{2}_F[0-9]{2}_(1|2)_V[0-9]',
    'SHATAU7'               : r'(SHATAU7_01_[A-Z]{4}_[0-9]{3}_(A|D|S|T|F)|SHATAU7_03_[A-Z]{4}_[0-9]{3})',
    'SHIELD_HD'             : r'SHIELD_HD_401_[0-9]{3}_(Screening|Qualification|EealyTermination|Week(48|96))',
    'SPARK'                 : r'SPARK_301_[0-9]{3}_(Week(24|52|60)|Unscheduled|EarlyTermination)',
    'SUCCES'                : r'RADIOSUCCESS_P[0-9]{2}_[A-Z]{3}',
    'TRIAL_21'              : r'TRIAL_21_[0-9]{3}',
}

def myprint(txtfile, str):
        print(str)
        txtfile.write(str+"\n")

def check_machine( regex_list, write_tsv, txtfile ):

    for project_name in regex_list.keys():

        # Get all exam for this protocol
        cur.execute( "SELECT label FROM xnat_subjectdata WHERE project='{}' ORDER BY demographics_xnat_abstractdemographicdata_id ASC".format(project_name) )
        exam_list = cur.fetchall()

        # for the stats
        N    = len(exam_list)
        good = 0
        bad  = 0

        myprint(txtfile, 'name in XNAT : {} // regex : {}'.format(project_name,regex_list[project_name]))
        myprint(txtfile, '======================================')

        # Check if all exam name is correct
        for exam_name in exam_list:

            clean_exam_name = str(exam_name).strip("(),'") # just get the string inside

            discard = re.search( '(pilot(e)?|phantom(e)?|test(e)?|fantom(e)?)', clean_exam_name, re.IGNORECASE )
            if (discard):
                N -= 1
                continue

            result = re.search( regex_list[project_name], clean_exam_name )

            if (result):
                display = ''
                good += 1
            else:
                display = ' <----------'
                bad += 1

            myprint(txtfile, "{}{}".format( clean_exam_name , display ))

        try:
            pct_good =  round(100*good/N)
        except ZeroDivisionError:
            pct_good = ''
        try:
            pct_bad =  round(100*bad/N)
        except ZeroDivisionError:
            pct_bad = ''

        myprint(txtfile, '======================================')
        myprint(txtfile,  "stats : N={} good={}({}%) bad={}({}%)".format( N, good, pct_good, bad, pct_bad )  )
        myprint(txtfile,  "\n" )

        write_tsv.writerow( [ project_name, regex_list[project_name], N, good, pct_good, bad, pct_bad ] )


main_path = '/network/lustre/iss01/cenir/analyse/irm/studies/cenir/nomenclatures'

# Write to .tsv
with open(os.path.join(main_path,'{}_table_verif_code_sujet_VerioPrisma.tsv'.format(now)),'w',newline='') as tsvfile:
    write_tsv = csv.writer(tsvfile,delimiter='\t')

    with open(os.path.join(main_path,'{}_list_verif_code_sujet_VerioPrisma.txt'.format(now)),'w',newline='') as txtfile:

        write_tsv.writerow(['Verio'])
        write_tsv.writerow( [ 'xnat_project_name', 'regex', 'N total', 'N good', '% good', 'N bad', '% bad' ] )
        check_machine(regex_verio, write_tsv, txtfile)
        write_tsv.writerow([])

        write_tsv.writerow(['Prisma'])
        write_tsv.writerow( [ 'xnat_project_name', 'regex', 'N total', 'N good', '% good', 'N bad', '% bad' ] )
        check_machine(regex_prisma, write_tsv,txtfile)

        txtfile.close()

    tsvfile.close()

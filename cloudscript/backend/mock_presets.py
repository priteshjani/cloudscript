# Mock presets for CloudScript Pharmacy Intelligence Demo

PRESETS = {
    "dorothy_thompson": {
        "id": "dorothy_thompson",
        "label": "Dorothy Thompson",
        "description": "Happy path - DOB + Insurance + NPI -> auto-verified, zero clicks",
        "status": "EQUAL",
        "rx_image": {
            "patient_name": "Dorothy Thompson",
            "dob": "02/14/1942",
            "insurance_id": "INS-100019",
            "zip_code": "77002",
            "gender": "Female",
            "medication": "Warfarin Sodium 5mg",
            "qty_days": "30 / 90d",
            "refills": "11",
            "prescriber": "Dr. James Wilson",
            "npi": "1234567890",
            "dea": "JW1234567"
        },
        "extracted_fields": {
            "patient_name": "Dorothy Thompson",
            "dob": "1942-02-14",
            "gender": "Female",
            "insurance_id": "INS-100019",
            "zip_code": "77002",
            "drug_name": "Warfarin Sodium",
            "strength": "5mg",
            "qty_days": "30 / 90d",
            "refills": "11",
            "prescriber": "Dr. James Wilson",
            "npi": "1234567890",
            "dea": "JW1234567"
        },
        "candidates": [
            {
                "id": "cand_dorothy_thompson",
                "name": "Dorothy Thompson",
                "dob": "1942-02-14",
                "insurance_id": "INS-100019",
                "npi": "1234567890",
                "zip": "77002",
                "gender": "Female",
                "score": 82,
                "tier": "GOOD",
                "signals": {
                    "dob": 100,
                    "name": 100,
                    "insurance": 100,
                    "npi": 0,  # Prior fill not found, but exact NPI verifies prescriber
                    "drug": 100,
                    "zip": 100,
                    "gender": 100,
                    "brand": 0
                },
                "trgm_score": 100,
                "vector_score": 100
            },
            {
                "id": "cand_dorothy_turner",
                "name": "Dorothy Turner",
                "dob": "1956-01-26",
                "insurance_id": "INS-879224828",
                "npi": "None",
                "zip": "77002",
                "gender": "Female",
                "score": 15,
                "tier": "POOR",
                "signals": {
                    "dob": 15,
                    "name": 45,
                    "insurance": 0,
                    "npi": 0,
                    "drug": 0,
                    "zip": 100,
                    "gender": 100,
                    "brand": 0
                },
                "trgm_score": 35,
                "vector_score": 24
            },
            {
                "id": "cand_thomas_rod",
                "name": "Thomas Rodriguez",
                "dob": "1987-03-15",
                "insurance_id": "INS-2049293187",
                "npi": "None",
                "zip": "77085",
                "gender": "Male",
                "score": 13,
                "tier": "POOR",
                "signals": {
                    "dob": 0,
                    "name": 10,
                    "insurance": 0,
                    "npi": 0,
                    "drug": 0,
                    "zip": 40,
                    "gender": 0,
                    "brand": 0
                },
                "trgm_score": 10,
                "vector_score": 14
            }
        ],
        "chatbot_log": "Match result: Dorothy Thompson - 82% confidence. Strong signals: DOB exact match, name match, insurance ID matches database. Looks good — I recommend verifying this match. Prescriber Dr. James Wilson verified via NPI exact match. Formula status: Warfarin Sodium 5mg is preferred generic (90% tier coverage, co-pay $3.40)."
    },
    "bob_smith": {
        "id": "bob_smith",
        "label": "Bob Smith -> Robert Smith",
        "description": "Nickname - pg_trgm misses, pgvector catches semantic similarity",
        "status": "FAIR",
        "rx_image": {
            "patient_name": "Bob Smith",
            "dob": "11/30/1980",
            "insurance_id": "INS-900223",
            "zip_code": "90210",
            "gender": "Male",
            "medication": "Metformin 500mg",
            "qty_days": "60 / 30d",
            "refills": "3",
            "prescriber": "Dr. Sarah Jenkins",
            "npi": "9876543210",
            "dea": "SJ9876543"
        },
        "extracted_fields": {
            "patient_name": "Bob Smith",
            "dob": "1980-11-30",
            "gender": "Male",
            "insurance_id": "INS-900223",
            "zip_code": "90210",
            "drug_name": "Metformin",
            "strength": "500mg",
            "qty_days": "60 / 30d",
            "refills": "3",
            "prescriber": "Dr. Sarah Jenkins",
            "npi": "9876543210",
            "dea": "SJ9876543"
        },
        "candidates": [
            {
                "id": "cand_robert_smith",
                "name": "Robert Smith",
                "dob": "1980-11-30",
                "insurance_id": "INS-900223",
                "npi": "9876543210",
                "zip": "90210",
                "gender": "Male",
                "score": 78,
                "tier": "GOOD",
                "signals": {
                    "dob": 100,
                    "name": 80,  # pgvector catches Bob = Robert nickname
                    "insurance": 100,
                    "npi": 100,
                    "drug": 90,
                    "zip": 100,
                    "gender": 100,
                    "brand": 0
                },
                "trgm_score": 20,  # low trigram string similarity
                "vector_score": 92  # high semantic vector similarity
            },
            {
                "id": "cand_bob_jones",
                "name": "Bob Jones",
                "dob": "1975-06-12",
                "insurance_id": "INS-440212",
                "npi": "None",
                "zip": "90210",
                "gender": "Male",
                "score": 32,
                "tier": "POOR",
                "signals": {
                    "dob": 10,
                    "name": 60,
                    "insurance": 0,
                    "npi": 0,
                    "drug": 0,
                    "zip": 100,
                    "gender": 100,
                    "brand": 0
                },
                "trgm_score": 50,
                "vector_score": 45
            }
        ],
        "chatbot_log": "Match result: Robert Smith - 78% confidence. The patient name on the prescription is 'Bob Smith' but the closest database match is 'Robert Smith'. pg_trgm string match scored poorly (20%), but the pgvector name embedding caught 'Bob' as a common nickname for 'Robert' with a 92% vector match score. Combined with exact DOB and Insurance matches, this is high confidence."
    },
    "prinivil_lisinopril": {
        "id": "prinivil_lisinopril",
        "label": "Prinivil -> Lisinopril",
        "description": "Brand-generic drug matching via product name embeddings",
        "status": "EQUAL",
        "rx_image": {
            "patient_name": "Liz Jones",
            "dob": "08/14/1972",
            "insurance_id": "INS-772091",
            "zip_code": "60611",
            "gender": "Female",
            "medication": "Prinivil 10mg",
            "qty_days": "30 / 30d",
            "refills": "5",
            "prescriber": "Dr. Alan Mercer",
            "npi": "1122334455",
            "dea": "AM1122334"
        },
        "extracted_fields": {
            "patient_name": "Liz Jones",
            "dob": "1972-08-14",
            "gender": "Female",
            "insurance_id": "INS-772091",
            "zip_code": "60611",
            "drug_name": "Prinivil",
            "strength": "10mg",
            "qty_days": "30 / 30d",
            "refills": "5",
            "prescriber": "Dr. Alan Mercer",
            "npi": "1122334455",
            "dea": "AM1122334"
        },
        "candidates": [
            {
                "id": "cand_elizabeth_jones",
                "name": "Elizabeth Jones",
                "dob": "1972-08-14",
                "insurance_id": "INS-772091",
                "npi": "1122334455",
                "zip": "60611",
                "gender": "Female",
                "score": 80,
                "tier": "GOOD",
                "signals": {
                    "dob": 100,
                    "name": 85,  # Liz -> Elizabeth vector match
                    "insurance": 100,
                    "npi": 100,
                    "drug": 95,
                    "zip": 100,
                    "gender": 100,
                    "brand": 100  # Generic matched successfully
                },
                "trgm_score": 30,
                "vector_score": 88
            }
        ],
        "chatbot_log": "Match result: Elizabeth Jones - 80% confidence. Brand substitution: The prescription specifies 'Prinivil 10mg', which is the brand name. The formulary recommends the generic equivalent 'Lisinopril 10mg'. The vector search matching confirmed that 'Prinivil' maps to 'Lisinopril' with high semantic mapping. I recommend switching to generic Lisinopril, which will reduce patient co-pay from $45.00 to $4.00."
    },
    "maria_insurance": {
        "id": "maria_insurance",
        "label": "Maria (Insurance)",
        "description": "3 Marias - Insurance ID resolver -> auto-verified",
        "status": "OTHER",
        "rx_image": {
            "patient_name": "Maria Garcia",
            "dob": "05/12/1990",
            "insurance_id": "INS-909012",
            "zip_code": "77019",
            "gender": "Female",
            "medication": "Amoxicillin 500mg",
            "qty_days": "20 / 10d",
            "refills": "0",
            "prescriber": "Dr. Carla Rossi",
            "npi": "4455667788",
            "dea": "CR4455667"
        },
        "extracted_fields": {
            "patient_name": "Maria Garcia",
            "dob": "1990-05-12",
            "gender": "Female",
            "insurance_id": "INS-909012",
            "zip_code": "77019",
            "drug_name": "Amoxicillin",
            "strength": "500mg",
            "qty_days": "20 / 10d",
            "refills": "0",
            "prescriber": "Dr. Carla Rossi",
            "npi": "4455667788",
            "dea": "CR4455667"
        },
        "candidates": [
            {
                "id": "cand_maria_garcia_1",
                "name": "Maria Garcia",
                "dob": "1990-05-12",
                "insurance_id": "INS-909012",
                "npi": "4455667788",
                "zip": "77019",
                "gender": "Female",
                "score": 85,
                "tier": "GOOD",
                "signals": {
                    "dob": 100,
                    "name": 100,
                    "insurance": 100,
                    "npi": 100,
                    "drug": 100,
                    "zip": 100,
                    "gender": 100,
                    "brand": 0
                },
                "trgm_score": 100,
                "vector_score": 100
            },
            {
                "id": "cand_maria_garcia_2",
                "name": "Maria Garcia",
                "dob": "1988-09-04",
                "insurance_id": "INS-304011",
                "npi": "None",
                "zip": "77019",
                "gender": "Female",
                "score": 38,
                "tier": "POOR",
                "signals": {
                    "dob": 0,
                    "name": 100,
                    "insurance": 0,
                    "npi": 0,
                    "drug": 0,
                    "zip": 100,
                    "gender": 100,
                    "brand": 0
                },
                "trgm_score": 100,
                "vector_score": 100
            }
        ],
        "chatbot_log": "Match result: Maria Garcia (INS-909012) - 85% confidence. There are multiple patients named 'Maria Garcia' in this zip code. However, the exact Insurance ID (INS-909012) resolved the match immediately. I've automatically selected candidate 1."
    },
    "maria_name_only": {
        "id": "maria_name_only",
        "label": "Maria (name only)",
        "description": "No secondary signals - unresolvable -> triggers callback review",
        "status": "DEMO",
        "rx_image": {
            "patient_name": "Maria Garcia",
            "dob": "05/12/1990",
            "insurance_id": "None",
            "zip_code": "None",
            "gender": "Female",
            "medication": "Ibuprofen 800mg",
            "qty_days": "90 / 30d",
            "refills": "2",
            "prescriber": "Dr. Carla Rossi",
            "npi": "None",
            "dea": "None"
        },
        "extracted_fields": {
            "patient_name": "Maria Garcia",
            "dob": "1990-05-12",
            "gender": "Female",
            "insurance_id": "None",
            "zip_code": "None",
            "drug_name": "Ibuprofen",
            "strength": "800mg",
            "qty_days": "90 / 30d",
            "refills": "2",
            "prescriber": "Dr. Carla Rossi",
            "npi": "None",
            "dea": "None"
        },
        "candidates": [
            {
                "id": "cand_maria_garcia_1",
                "name": "Maria Garcia",
                "dob": "1990-05-12",
                "insurance_id": "INS-909012",
                "npi": "None",
                "zip": "77019",
                "gender": "Female",
                "score": 45,
                "tier": "FAIR",
                "signals": {
                    "dob": 100,
                    "name": 100,
                    "insurance": 0,
                    "npi": 0,
                    "drug": 0,
                    "zip": 0,
                    "gender": 100,
                    "brand": 0
                },
                "trgm_score": 100,
                "vector_score": 100
            },
            {
                "id": "cand_maria_garcia_2",
                "name": "Maria Garcia",
                "dob": "1988-09-04",
                "insurance_id": "INS-304011",
                "npi": "None",
                "zip": "77019",
                "gender": "Female",
                "score": 38,
                "tier": "POOR",
                "signals": {
                    "dob": 0,
                    "name": 100,
                    "insurance": 0,
                    "npi": 0,
                    "drug": 0,
                    "zip": 0,
                    "gender": 100,
                    "brand": 0
                },
                "trgm_score": 100,
                "vector_score": 100
            }
        ],
        "chatbot_log": "Match result: Unresolved. There are multiple 'Maria Garcia' patients in the database, but no Insurance ID or NPI history is provided on this prescription. I cannot automatically resolve this match. This has been flagged for manual verification."
    }
}

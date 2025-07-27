import json
from datetime import datetime

def save_output_json(data, output_path, persona, job, pdfs, exec_time=None):
    """
    Writes the final JSON output with correct field names.
    Accepts records with either 'page' or 'page_number'.
    """
    output = {
        "metadata": {
            "input_documents": pdfs,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    
    for d in data:
        page_num = d.get("page") or d.get("page_number")
        output["extracted_sections"].append({
            "document":        d["document"],
            "section_title":   d["section_title"],
            "importance_rank": d["importance_rank"],
            "page_number":     page_num
        })

   
    for d in data:
        page_num = d.get("page") or d.get("page_number")
        output["subsection_analysis"].append({
            "document":    d["document"],
            "refined_text": d["refined_text"],
            "page_number": page_num
        })

   
    if exec_time is not None:
        output["metadata"]["execution_time_sec"] = round(exec_time, 2)

    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

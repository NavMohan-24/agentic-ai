from unidiff import PatchSet
from langchain_core.documents import Document

def create_pr_document_from_patch(patch):

    patch_set = PatchSet.from_string(patch)

    # filtered_patch_set = [
    # patched_file for patched_file in patch_set
    # if 'test' not in patched_file.path
    # ]

    all_hunk_texts = []
    files_changed = []

    #date = []

    commit_messages = []
    if "Subject: " in patch:
        for line in patch.split('\n'):
                if line.startswith("Subject: "):
                    cm = line.replace("Subject: ", "").strip()
                    commit_messages.append(cm)
    
    for patched_file in patch_set:
        files_changed.append(patched_file.path)
        for hunk in patched_file:
            all_hunk_texts.append(str(hunk))

    page_content = "\n\n".join(all_hunk_texts)
    
    # Create the metadata dictionary for the entire pull request
    metadata = {
        "commit_message": commit_messages,
        "files_changed": files_changed,
        "num_files_changed": len(files_changed),
        # You could add other info like author, date, etc.
    }
    
    # Create and return the single Document object
    return Document(page_content=page_content, metadata=metadata)




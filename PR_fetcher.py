import requests

def get_release_info(owner, repo, tag_name, token):
    """
    Gets the details for a specific GitHub release by its tag name.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag_name}"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_previous_release_info(owner, repo, token):
    """
    Finds the latest and previous release to establish a comparison range.
    Returns the SHA of the latest and previous release tags.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    releases = response.json()
    
    # Filter out draft and prerelease versions if necessary
    published_releases = [r for r in releases if not r.get('draft') and not r.get('prerelease')]
    
    if len(published_releases) < 2:
        # If there's only one release, compare to the default branch head
        latest_tag = published_releases[0]['tag_name']
        previous_tag = published_releases[0]['target_commitish'] # The default branch
        return latest_tag, previous_tag
    
    latest_release = published_releases[0]
    previous_release = published_releases[1]
    
    return latest_release['tag_name'], previous_release['tag_name']

def get_commits_between_tags(owner, repo, base_tag, head_tag, token):
    """
    Gets a list of commits between a base and head tag.
    
    This function now includes more robust error handling to help with debugging.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base_tag}...{head_tag}"
    headers = {'Authorization': f'Bearer {token}'}
    
    # This try/except block is new and should help you debug the issue.
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('commits', [])
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching commits from the API: {e}")
        print(f"URL: {url}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        return []


def get_prs_for_commit(owner, repo, commit_sha, token):
    """
    Finds pull requests associated with a specific commit SHA.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}/pulls"
    headers = {
        'Authorization': f'Bearer {token}',       
        'Accept': 'application/vnd.github.v3+json' # Use a specific media type to get PRs ,
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_prs_for_release(owner, repo, token):
    """
    Main function to orchestrate the process.
    """
    try:
        print("Fetching release information...")
        latest_tag, previous_tag = get_previous_release_info(owner, repo, token)
        print(f"Comparing changes between '{previous_tag}' and '{latest_tag}'")
        
        print("Fetching commits...")
        commits = get_commits_between_tags(owner, repo, previous_tag, latest_tag, token)
        
        if not commits:
            print("No commits found between these tags. This may be due to a recent API error, check the logs above.")
            return

        print(f"Found {len(commits)} commits.")
        
        all_prs = set() # Use a set to avoid duplicates

        # Step 3: Find PRs for each commit
        for commit in commits:
            commit_sha = commit['sha']
            prs_for_commit = get_prs_for_commit(owner, repo, commit_sha, token)
            for pr in prs_for_commit:
                all_prs.add((pr['number'], pr['title']))
        
        if all_prs:
            print("\n--- Associated Pull Requests ---")
            for pr_number, pr_title in sorted(list(all_prs)):
                print(f"  - PR #{pr_number}: {pr_title}")
            return all_prs
        else:
            print("\nNo associated pull requests found.")

    except requests.exceptions.HTTPError as e:
        print(f"An API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
def get_pr_by_number(owner, repo, pr_number, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json' # This is the default format for getting PR details
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status() # Raises an exception for bad status codes
    
    return response.json()    



if __name__ == "__main__":
    REPO_OWNER = "Qiskit"
    REPO_NAME = "qiskit-addon-aqc-tensor"
    GITHUB_TOKEN = ''
    get_prs_for_release(REPO_OWNER, REPO_NAME, GITHUB_TOKEN)
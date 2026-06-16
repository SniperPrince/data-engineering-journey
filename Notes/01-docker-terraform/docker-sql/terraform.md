# Terraform — Complete Module Notes

## Part 1: What Terraform Is And Why It Exists

### The problem
Cloud infrastructure has dozens of resources: buckets, datasets, IAM roles, VMs, networks, permissions. Creating these by clicking through web UI is:
- Not reproducible (you forget what you did)
- Not reviewable (no PRs for clicks)
- Not version-controlled
- Not shareable with teammates

### The solution
**Terraform** is an Infrastructure-as-Code (IaC) tool. You describe infrastructure
in `.tf` files (in HCL language), commit to git, and Terraform creates/updates/destroys
the actual cloud resources to match your file.

The `.tf` file = your spec
Terraform = the worker that makes reality match your spec
Cloud (GCP/AWS/Azure) = the actual infrastructure

### Key benefit
Same `.tf` file → identical infrastructure on dev, staging, prod. No drift. No "works on my account."

---

## Part 2: The 4 Core Commands (You Will Type These Forever)

| Command | What it does | When to run |
|---|---|---|
| `terraform init` | Downloads provider plugins (e.g. google plugin), creates `.terraform/` folder, generates `.terraform.lock.hcl` | Once per project. Re-run if you add a new provider. |
| `terraform plan` | Dry run — shows what would change if you applied. No actual changes. | Before every apply. Treat it like `git diff`. |
| `terraform apply` | Actually creates/updates/destroys resources to match `.tf` files | When you're ready to commit changes |
| `terraform destroy` | Removes ALL resources Terraform manages | When done experimenting. **DO THIS** to avoid GCP costs. |

Bonus useful commands:
- `terraform fmt` — auto-formats your `.tf` files (like prettier for code)
- `terraform validate` — checks syntax without contacting the cloud
- `terraform show` — shows what's currently in the state file

---

## Part 3: The File Anatomy

A typical Terraform project has:

project/
├── main.tf              ← Resources you want to create
├── variables.tf         ← Input variables
├── .terraform.lock.hcl  ← Locks provider versions (commit to git ✅)
├── terraform.tfstate    ← State file (NEVER commit ❌)
├── terraform.tfstate.backup  ← Auto-backup of state (NEVER commit ❌)
└── .terraform/          ← Downloaded plugins (NEVER commit ❌)

`.gitignore` should contain:
.terraform/
*.tfstate
*.tfstate.backup

---

## Part 4: main.tf — The Three Block Types

### 4.1 The `terraform` block
Declares which providers you need and their versions.

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}
```

**Why pin version?** Same reason as `uv.lock` in Module 1.2 — reproducibility. Without pinning, a Terraform version bump could break your config silently.

### 4.2 The `provider` block
Configures the actual cloud connection.

```hcl
provider "google" {
  project = "your-gcp-project-id"
  region  = "us-central1"
}
```

- `project` = your GCP project ID (the unique one from GCP console)
- `region` = which datacenter region to use

### 4.3 The `resource` block (the heart of Terraform)
Each resource describes one cloud thing you want.

```hcl
resource "google_storage_bucket" "demo_bucket" {
  name          = "my-data-bucket-xyz123"
  location      = "US"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}
```

**Understanding the structure:**
- `resource` = keyword (always)
- `"google_storage_bucket"` = the resource TYPE (defined by the google provider)
- `"demo_bucket"` = your LOCAL name for it (used to reference within Terraform)
- Inside `{}` = the configuration: name, location, options, etc.

**The two names confusion:**
- `"demo_bucket"` (after the type) = how Terraform refers to it internally
- `name = "my-data-bucket-xyz123"` (inside the block) = what the bucket is actually called on GCP

You can reference this bucket elsewhere in `.tf` files as `google_storage_bucket.demo_bucket.name`.

### Example: BigQuery Dataset

```hcl
resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = "demo_dataset"
  location   = "US"
}
```

Same pattern. Different type. That's the magic of Terraform — once you know the pattern, every cloud resource follows it.

---

## Part 5: variables.tf — Parameterizing Your Config

Hardcoding `project = "my-project-id"` is bad practice. Use variables instead.

### Declaring variables
```hcl
variable "project" {
  description = "Your GCP Project ID"
  type        = string
}

variable "region" {
  description = "Region for GCP resources"
  default     = "us-central1"
  type        = string
}

variable "bucket_name" {
  description = "GCS Bucket Name"
  default     = "my-data-bucket"
  type        = string
}
```

Variable block fields:
- `description` — for documentation
- `default` — value if user doesn't pass one. If omitted, Terraform will prompt or error.
- `type` — string, number, bool, list, map, etc. Catches type errors early.

### Using variables in main.tf
```hcl
provider "google" {
  project = var.project
  region  = var.region
}

resource "google_storage_bucket" "demo_bucket" {
  name     = var.bucket_name
  location = var.region
}
```

The pattern: `var.<variable_name>`. Always prefix with `var.`.

### Passing variable values (3 ways, choose one)

**Option A: Prompt at runtime**
Don't set `default`. Terraform asks you each time:

terraform plan

var.project
Enter a value: my-gcp-project-123

**Option B: CLI flag**
```bash
terraform plan -var="project=my-gcp-project-123"
terraform apply -var="project=my-gcp-project-123"
```

**Option C: terraform.tfvars file**
Create `terraform.tfvars` (auto-loaded by Terraform):
```hcl
project = "my-gcp-project-123"
region  = "us-central1"
```

**Don't commit `.tfvars`** — add to `.gitignore`. They often contain project IDs or secrets.

---

## Part 6: tfstate — The Concept That Confuses Everyone

`terraform.tfstate` is Terraform's **memory of what it owns**.

### What's in it
A JSON file mapping your `.tf` resources to real-world cloud objects:

"google_storage_bucket.demo_bucket" → bucket ID "my-data-bucket-xyz123" on GCP
"google_bigquery_dataset.demo_dataset" → dataset ID "demo_dataset" on GCP

### Why it matters
On next `terraform apply`, Terraform reads tfstate to know:
- "I already created the bucket. Don't create another."
- "The dataset doesn't exist anymore (someone deleted it manually). I need to recreate it."

Without tfstate, every `apply` would create duplicates or fail.

### `terraform.tfstate.backup`
Auto-created backup of previous state. Useful if state file gets corrupted.

### When does state change?
- `terraform apply` updates state after each resource is created/modified
- `terraform destroy` removes resources from state
- `terraform plan` reads state but doesn't change it

### Critical rules for state
1. **NEVER commit to git** — state files can contain sensitive info (API keys, IPs, etc.)
2. **NEVER edit by hand** — use `terraform state` commands if you must
3. **Production teams store state remotely** (in GCS / S3) so the team shares one state. For our learning, local file is fine.

---

## Part 7: GCP Authentication (ADC)

For Terraform to act on GCP, it needs credentials. The modern way is **Application Default Credentials (ADC)**.

### Setup once
```bash
gcloud auth application-default login
```

This:
1. Opens browser
2. You log in with your Google account
3. Saves credentials to `~/.config/gcloud/application_default_credentials.json`
4. Any tool (including Terraform) using ADC will use these creds automatically

### Alternative: Service Account JSON Key
For production / automation:
1. Create service account in GCP console
2. Grant it roles (Storage Admin, BigQuery Admin, etc.)
3. Download JSON key
4. Set env var:
```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
```

For Zoomcamp learning, ADC (the `gcloud auth` method) is enough.

---

## Part 8: The Complete Workflow (What You Did In The Module)

Create GCP project in console
Run: gcloud auth application-default login
Write main.tf + variables.tf
terraform init                         # download google provider
terraform fmt                          # tidy up formatting
terraform plan -var="project=..."      # dry run
terraform apply -var="project=..."     # actually create
(Check GCP console — bucket & dataset exist!)
terraform destroy                      # tear down to avoid costs


This entire cycle is the loop you'll use forever in IaC work.

---

## Part 9: What Goes Into Git vs What Doesn't

| File | Commit? | Why |
|---|---|---|
| `main.tf` | ✅ Yes | Your spec, must be versioned |
| `variables.tf` | ✅ Yes | Same |
| `.terraform.lock.hcl` | ✅ Yes | Pins provider versions — reproducibility |
| `terraform.tfvars` | ❌ No | Often contains project IDs / secrets |
| `terraform.tfstate` | ❌ No | Sensitive + auto-generated |
| `terraform.tfstate.backup` | ❌ No | Same |
| `.terraform/` folder | ❌ No | Downloaded plugins, regenerable |

Standard `.gitignore` for Terraform:

.terraform/
*.tfstate
*.tfstate.backup
*.tfvars


---

## Part 10: For Resume + Interviews

### Resume bullet (what you actually did)
> Provisioned GCP infrastructure using Terraform: GCS buckets and BigQuery datasets,
> with parameterized configurations via variables.tf and version-pinned providers.

### Interview Q&A you should be able to answer

**Q: What is Infrastructure as Code?**
> Declarative description of cloud resources in version-controllable files. Replaces manual UI clicks for reproducibility and team collaboration.

**Q: What does Terraform do?**
> Reads .tf files, compares to current cloud state, plans changes, then executes them via cloud APIs. Maintains a state file as memory of what it manages.

**Q: What's the tfstate file?**
> Terraform's memory mapping declarations in .tf files to real cloud objects. Used to detect drift and know what to update/destroy. Never committed to git; sensitive.

**Q: What's the difference between `terraform plan` and `apply`?**
> Plan = dry run, shows what changes would happen, doesn't touch infrastructure. Apply = actually executes the changes. Always plan before apply in production.

**Q: How do you handle secrets in Terraform?**
> Never hardcode. Use variables loaded from .tfvars files (gitignored), environment variables, or secret managers (e.g. GCP Secret Manager, AWS Secrets Manager).

**Q: How does Terraform authenticate to GCP?**
> Either Application Default Credentials (`gcloud auth application-default login`) for local dev, or a service account JSON key (env var `GOOGLE_APPLICATION_CREDENTIALS`) for production.

---

## Part 11: Common Gotchas

1. **Forgot `terraform destroy` before turning off laptop** — resources keep running on GCP. Set budget alerts!
2. **Committed tfstate to git** — security leak. If this happens, rotate any credentials in the state.
3. **Edited resources via GCP console after Terraform created them** — causes drift. Next `apply` may undo your manual changes. Always edit via Terraform.
4. **Provider version not pinned** — works today, breaks tomorrow. Always pin in the terraform block.
5. **Hardcoded project ID in main.tf** — use variables instead.
6. **`terraform apply` without `plan` first** — surprises in production. Always plan first.

---

## Part 12: The Mental Model To Remember

Three things make Terraform click:

1. **Declare what you want, not how to make it.** Write the end state in `.tf` files. Terraform figures out the API calls.

2. **State is the source of truth for what Terraform owns.** Treat it like Git's `.git` folder — sacred, machine-managed, don't touch.

3. **Providers translate generic concepts to cloud-specific APIs.** Same Terraform skill applies to AWS, GCP, Azure — only the provider and resource types change.

---

## Final Note On Syntax Memorization

You don't need to memorize HCL syntax. Real Terraform work:
- 30% writing new resources (lookup docs every time)
- 30% modifying existing configs (lookup syntax)
- 20% debugging state issues (very few people memorize these)
- 20% running plan/apply/destroy commands (memorize these — used daily)

Memorize the **concepts**, **commands**, and **structure**. Look up specific resource arguments every time. That's how senior engineers actually work.
# CiviQual Stats v2.0.0 — Deployment Guide

**Updated:** April 21, 2026
**Edition:** DMAIC

This guide is the authoritative reference for building, signing, and
releasing CiviQual Stats v2.0.0. It replaces the v1.0.0 instructions.

---

## 1. Prerequisites

Install the following on your Windows 10 or 11 build machine:

| Component | Version | Notes |
|---|---|---|
| Python | 3.11 or later | Add to PATH. Required to run the app from source and to sign licenses. |
| WiX Toolset | v5.0 or later | The `wix` command must be on PATH. |
| Windows SDK | 10.0.22621 or later | Provides `signtool.exe`. |
| Certum code-signing certificate | Installed in the current user store | Thumbprint: `E6830B627AF1AD8980FADDF221D27FAE361A166D` |
| Git | Any recent version | For tagging releases. |

Optional but recommended:

- Visual Studio Code or any editor with Python integration.
- A clean test machine (a fresh Windows VM is ideal) for install validation.

---

## 2. One-time setup

### 2.1 Generate the Pro license key pair

```cmd
cd scripts
python generate_keys.py --generate-keys
```

This creates `%USERPROFILE%\.civiqual_keys\civiqual_private.pem` and
`civiqual_public.pem`. The script prints the public key; copy it into the
clipboard **or** use the helper in the next step.

### 2.2 Inject the public key into `license_manager.py`

```cmd
cd ..
python scripts\update_pubkey.py "%USERPROFILE%\.civiqual_keys\civiqual_public.pem"
```

Confirm the `PUBLIC_KEY_PEM` block in `license_manager.py` now contains the
production key.

### 2.3 Back up the key pair

```cmd
mkdir "C:\Users\%USERNAME%\OneDrive\Step in the Right Direction\CiviQual\Keys"
copy "%USERPROFILE%\.civiqual_keys\*.pem" ^
     "C:\Users\%USERNAME%\OneDrive\Step in the Right Direction\CiviQual\Keys\"
```

The private key is the single most sensitive asset of the product. If it is
lost, every existing Pro license becomes unverifiable.

---

## 3. Building the application

### 3.1 Verify dependencies

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The application should launch with the DMAIC phase tabs visible. Load any
sample from the `samples` folder to confirm basic behavior, then close.

### 3.2 Run the automated build

From the repository root:

```cmd
scripts\build.cmd
```

The script performs four steps:

1. Builds `CiviQualStats_2.0.0_PerUser.msi` with WiX.
2. Builds `CiviQualStats_2.0.0_PerMachine.msi` with WiX.
3. Signs the per-user MSI with the Certum certificate.
4. Signs the per-machine MSI with the Certum certificate.

If any step fails, the script exits with a non-zero code and prints the
error. Common causes are listed in Section 7.

---

## 4. Validating the build

### 4.1 Signature check

```cmd
signtool verify /pa /v CiviQualStats_2.0.0_PerUser.msi
signtool verify /pa /v CiviQualStats_2.0.0_PerMachine.msi
```

Both should report `Successfully verified`.

### 4.2 Per-user install test

1. Copy the per-user MSI to a test machine.
2. Double-click it. The installer should run without administrator prompts.
3. Confirm the install path is
   `%LOCALAPPDATA%\A Step in the Right Direction, LLC\CiviQual Stats`.
4. Run `scripts\verify.cmd` to confirm every module is present.
5. Launch from the Start menu. The license status should read "Free".

### 4.3 Per-machine install test

1. Run the per-machine MSI on a separate VM with administrator rights.
2. Confirm the install path is
   `%ProgramFiles%\A Step in the Right Direction, LLC\CiviQual Stats`.
3. Confirm launch from both administrator and standard accounts.

### 4.4 Pro license test

```cmd
python scripts\generate_keys.py --sign --licensee "Test User" ^
    --expires 2027-12-31 --out test_license.json
```

Install `test_license.json` via the application's **License → Install License
File…** menu. Restart the application. Every Pro sub-tab should now be
populated with live panels (not the locked placeholder).

### 4.5 Pro module smoke tests

Load the Pro sample files in sequence and confirm each panel renders:

- `pro_01_gage_rr.csv` → Measure tab → MSA
- `pro_02_doe_factorial.csv` → Analyze tab → DOE
- `pro_03_regression.csv` → Analyze tab → Regression
- `pro_04_two_sample_t.csv` → Analyze tab → Hypothesis Tests
- `pro_05_cusum_example.csv` → Control tab → CUSUM / EWMA
- `pro_06_fmea_seed.csv` → Control tab → Planning Tools
- `pro_07_nonnormal_capability.csv` → Measure tab → Adv Capability (enable Box-Cox)

---

## 5. GitHub release

### 5.1 Commit and tag

```cmd
git add -A
git commit -m "Release v2.0.0 - DMAIC Edition"
git tag -a v2.0.0 -m "CiviQual Stats v2.0.0 - DMAIC Edition"
git push origin main
git push origin v2.0.0
```

### 5.2 Publish the release

1. Open `https://github.com/qualityincourts-lab/CiviQual/releases/new`.
   (If the repository is still named `WatsonLSS`, rename it first under
   **Settings → General**.)
2. Select tag `v2.0.0`.
3. Title: `CiviQual Stats 2.0.0 - DMAIC Edition`.
4. Paste the contents of `CHANGELOG.md` for v2.0.0 into the body.
5. Attach both signed MSIs.
6. Publish.

### 5.3 Update the download page

Point `qualityincourts.com` downloads to the new release URLs. The per-user
MSI should be the primary recommendation; the per-machine MSI should be
offered as "for IT-managed installations".

---

## 6. Issuing Pro licenses

For each customer:

```cmd
python scripts\generate_keys.py --sign ^
    --licensee "Customer Name or Email" ^
    --expires 2027-12-31 ^
    --out "licenses\customer_YYYYMMDD.json"
```

Omit `--expires` for a perpetual license. Keep a copy of every issued
license file in a secure location; losing the file prevents reissuing an
identical license_id.

---

## 7. Troubleshooting

### WiX error: `cannot find file`
The `<File>` elements reference paths relative to the `.wxs` file. Run
`wix build` from the repository root, not from a subdirectory.

### WiX error: undefined preprocessor variable `Scope`
Invoke `wix build` with `-d Scope=perUser` or `-d Scope=perMachine`.
The automated script does this correctly.

### Import errors at app launch
Run `python main.py` directly. Typical causes:

- Missing dependency. Run `pip install -r requirements.txt`.
- A Pro module import error. The application tolerates these by showing the
  error in place of the tool; check the placeholder for the trace.

### License installed but Pro tools still locked
- The application only loads the license at startup. Close and relaunch.
- Run **License → License Status…** to see the diagnostic. "Signature
  invalid" means the license was signed with a different private key than
  the one whose public key is embedded in `license_manager.py`.

### `signtool` not found
Add the Windows SDK `x64` bin folder to PATH or edit the `SIGNTOOL`
variable at the top of `scripts\build.cmd`.

### High-DPI rendering is off
Ensure the app is launched from a shortcut or the MSI installer; running
loose `python main.py` without the `QT_AUTO_SCREEN_SCALE_FACTOR` environment
variable can render plots at incorrect sizes on 4K displays.

---

## 8. Post-release checklist

- [ ] Both MSIs uploaded to the GitHub release.
- [ ] Download page on `qualityincourts.com` updated.
- [ ] `civiqual.com` domain pointing to the download page (once registered).
- [ ] USPTO trademark application filed for CiviQual (Class 9 and 42).
- [ ] Announcement drafted for the Quality in Courts Substack newsletter.
- [ ] Version number on `version.py` confirmed for the next development
      cycle (v2.1.0-dev).

---

## 9. Rollback plan

If a released MSI must be withdrawn:

1. Delete the release asset on GitHub.
2. Replace the download link on the website with the previous version.
3. Leave the git tag in place; create a new patch release (for example,
   v2.0.1) rather than rewriting history.

A signed MSI cannot be "unsigned" once distributed. If the compromise is
severe enough to warrant certificate revocation, contact Certum and follow
their revocation procedure; issue new installers with a fresh certificate.

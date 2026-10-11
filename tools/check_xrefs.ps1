# Cross-document reference checks; writes /CROSS_REFERENCES.md (see check_xrefs.py).
python (Join-Path $PSScriptRoot 'check_xrefs.py') @args
exit $LASTEXITCODE

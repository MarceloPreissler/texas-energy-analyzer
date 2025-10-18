Write-Output "Monitoring Railway data scraping job..."
Write-Output "This will take 5-10 minutes as Playwright scrapes real data"
Write-Output ""

for ($i=1; $i -le 15; $i++) {
    Write-Output "=== Check $i/15 - $(Get-Date -Format 'HH:mm:ss') ==="

    try {
        $plans = Invoke-RestMethod -Uri 'https://web-production-665ac.up.railway.app/plans'
        $count = $plans.Count
        Write-Output "Total plans in database: $count"

        if ($count -gt 50) {
            Write-Output ""
            Write-Output "SUCCESS! Data loaded ($count plans)"
            Write-Output ""
            Write-Output "Checking data quality..."

            # Check for fake data
            $commercial = Invoke-RestMethod -Uri 'https://web-production-665ac.up.railway.app/plans?service_type=Commercial'
            $commercialCount = $commercial.Count
            $fake = $commercial | Where-Object { $_.special_features -like "*verify*" -or $_.special_features -like "*Typical*" }
            $fakeCount = ($fake | Measure-Object).Count

            Write-Output ""
            Write-Output "Commercial Plans Analysis:"
            Write-Output "  Total commercial: $commercialCount"
            Write-Output "  Fake plans (with 'verify'/'Typical'): $fakeCount"
            Write-Output "  Real plans: $($commercialCount - $fakeCount)"
            Write-Output ""

            if ($fakeCount -eq 0) {
                Write-Output "[SUCCESS] All data is REAL - no fake plans detected!"
            } else {
                Write-Output "[WARNING] Found $fakeCount fake plans - cleanup needed"
            }

            break
        }
    } catch {
        Write-Output "Database still empty or loading... (scraper running)"
    }

    Write-Output ""

    if ($i -lt 15) {
        Write-Output "Waiting 30 seconds for next check..."
        Start-Sleep -Seconds 30
    }
}

Write-Output ""
Write-Output "Monitoring complete!"

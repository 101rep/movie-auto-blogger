[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ws = New-Object -ComObject WScript.Shell
$desktop = "C:\Users\ktaeh\OneDrive\바탕 화면"
$antigravity = "C:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티"
$movie = "$antigravity\movie-auto-blogger"
$toon = "$antigravity\ToonForge_Desktop_Windows"
$company = "C:\Users\ktaeh\OneDrive\바탕 화면\앱_개발_마스터회사"
$threads = "C:\Users\ktaeh\OneDrive\바탕 화면\쓰레드_계정별_접속기"
$insta = "C:\Users\ktaeh\OneDrive\바탕 화면\InstagramAI"

$items = @(
    @{
        Name = "Threads x 쿠팡 자동화.lnk"
        Target = "$antigravity\start_threads_automation.bat"
        WorkDir = $antigravity
        Icon = "$env:SystemRoot\system32\shell32.dll,220"
        Desc = "Threads x 쿠팡 파트너스 AI 자동화 시스템 (Port 8080)"
    },
    @{
        Name = "Movie Auto Blogger.lnk"
        Target = "$movie\start_app.bat"
        WorkDir = $movie
        Icon = "$env:SystemRoot\system32\imageres.dll,67"
        Desc = "무비 오토 블로거 관리자 대시보드 (Port 8000)"
    },
    @{
        Name = "ToonForge 스튜디오.lnk"
        Target = "$toon\ToonForge.exe"
        WorkDir = $toon
        Icon = "$toon\ToonForge.exe,0"
        Desc = "ToonForge Desktop Studio v2.0 (인스타툰 & 카드뉴스 제작기)"
    },
    @{
        Name = "멍당근 펫케어 앱.lnk"
        Target = "$antigravity\펫케어_앱_실행하기.bat"
        WorkDir = $antigravity
        Icon = "$env:SystemRoot\system32\imageres.dll,102"
        Desc = "멍당근 펫케어 & 나눔 마켓 모바일 웹앱 (Port 8088)"
    },
    @{
        Name = "가상직원 3명 AI 스튜디오.lnk"
        Target = "$antigravity\가상직원3명_스튜디오_실행.bat"
        WorkDir = $antigravity
        Icon = "$env:SystemRoot\system32\imageres.dll,26"
        Desc = "가상직원 3명(큐레이터/스토리작가/디자이너) 자율 파이프라인"
    },
    @{
        Name = "텔레그램 링크 배달원.lnk"
        Target = "$antigravity\텔레그램_중간직원_실행.bat"
        WorkDir = $antigravity
        Icon = "C:\Users\ktaeh\AppData\Roaming\Telegram Desktop\Telegram.exe,0"
        Desc = "텔레그램 쇼핑 링크 실시간 감지 및 자동 제작 쿠리어 봇"
    },
    @{
        Name = "AI 앱개발 마스터회사.lnk"
        Target = "$company\START_SERVER.bat"
        WorkDir = $company
        Icon = "$env:SystemRoot\system32\imageres.dll,114"
        Desc = "AI Company OS - 자율 소프트웨어 개발사 (Port 3000)"
    },
    @{
        Name = "쓰레드 7개 계정 원클릭 접속기.lnk"
        Target = "$threads\통합_계정접속기.bat"
        WorkDir = $threads
        Icon = "$env:SystemRoot\system32\shell32.dll,15"
        Desc = "Threads 7개 부계정 독립 세션 원클릭 자동 접속기"
    },
    @{
        Name = "Instagram AI 떡상 탐색기.lnk"
        Target = "$insta\run_app.bat"
        WorkDir = $insta
        Icon = "$env:SystemRoot\system32\imageres.dll,109"
        Desc = "Instagram AI Viral Localization Toolkit"
    },
    @{
        Name = "Cloudways 서버 원클릭 동기화.lnk"
        Target = "$antigravity\서버_원클릭_동기화.bat"
        WorkDir = $antigravity
        Icon = "$env:SystemRoot\system32\shell32.dll,146"
        Desc = "Cloudways 운영 서버 최신 코드 및 DB 원클릭 동기화"
    }
)

foreach ($item in $items) {
    $lnkPath = Join-Path $desktop $item.Name
    $s = $ws.CreateShortcut($lnkPath)
    $s.TargetPath = $item.Target
    $s.WorkingDirectory = $item.WorkDir
    if ($item.Icon) {
        $s.IconLocation = $item.Icon
    }
    $s.Description = $item.Desc
    $s.Save()
    Write-Host "Created shortcut: $($item.Name)"
}

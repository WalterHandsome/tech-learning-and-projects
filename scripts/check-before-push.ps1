# 上传前安全检查脚本 (PowerShell)
# 使用方法: .\scripts\check-before-push.ps1

Write-Host "🔍 开始安全检查..." -ForegroundColor Yellow

$errors = 0

# 检查敏感文件
Write-Host "`n检查敏感文件..." -ForegroundColor Yellow
$sensitivePatterns = @(
    ".env",
    "private-notes",
    "*secret*",
    "*password*",
    "*.pem",
    "*.ppk"
)

$stagedFiles = git diff --cached --name-only 2>$null
if ($stagedFiles) {
    foreach ($pattern in $sensitivePatterns) {
        $matches = $stagedFiles | Where-Object { $_ -like $pattern }
        if ($matches) {
            Write-Host "❌ 发现敏感文件: $pattern" -ForegroundColor Red
            $errors++
        }
    }
}

# 检查 .gitignore
Write-Host "`n检查 .gitignore..." -ForegroundColor Yellow
if (-not (Test-Path ".gitignore")) {
    Write-Host "❌ 缺少 .gitignore 文件" -ForegroundColor Red
    $errors++
} else {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -notmatch "private-notes") {
        Write-Host "⚠️  .gitignore 中未排除 private-notes" -ForegroundColor Yellow
    } else {
        Write-Host "✅ .gitignore 配置正确" -ForegroundColor Green
    }
}

# 检查将要提交的文件
Write-Host "`n检查将要提交的文件..." -ForegroundColor Yellow
$status = git status --porcelain 2>$null
if ($status) {
    Write-Host "将要提交的文件:" -ForegroundColor Cyan
    $status | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "✅ 没有待提交的文件" -ForegroundColor Green
}

# 总结
Write-Host "`n检查完成" -ForegroundColor Yellow
if ($errors -eq 0) {
    Write-Host "✅ 安全检查通过，可以安全推送" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ 发现 $errors 个问题，请修复后再推送" -ForegroundColor Red
    exit 1
}


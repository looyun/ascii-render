# ascii-render 一键脚本

一行命令在任意平台下载并运行 ascii-render。

## 使用方法

### Linux / macOS / WSL

```bash
# 默认示例（爱你.gif）
bash <(curl -sL https://raw.githubusercontent.com/looyun/ascii-render/master/scripts/demo.sh)

# 指定版本和输入
bash <(curl -sL https://raw.githubusercontent.com/looyun/ascii-render/master/scripts/demo.sh) latest /path/to/image.gif

# 或保存脚本后执行
curl -sL https://raw.githubusercontent.com/looyun/ascii-render/master/scripts/demo.sh -o demo.sh
bash demo.sh
bash demo.sh latest https://example.com/love.gif
```

### Windows (PowerShell)

```powershell
# 默认示例（爱你.gif）
irm https://raw.githubusercontent.com/looyun/ascii-render/master/scripts/demo.ps1 | iex

# 指定版本和输入
$input = "https://example.com/love.gif"
irm https://raw.githubusercontent.com/looyun/ascii-render/master/scripts/demo.ps1 | iex -Version latest -Input $input

# 或保存脚本后执行
irm https://raw.githubusercontent.com/looyun/ascii-render/master/scripts/demo.ps1 -OutFile demo.ps1
.\demo.ps1
.\demo.ps1 -Version latest -Input "https://example.com/love.gif"
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `Version` | 发布的版本标签，如 `v0.1.0` 或 `latest` | `latest` |
| `Input` | 图片/ GIF /视频路径或 URL | 爱你.gif |

## 示例

```bash
# 渲染本地 GIF
bash demo.sh latest ./my-image.gif

# 渲染网络 GIF
bash demo.sh latest https://example.com/animation.gif

# 渲染图片
bash demo.sh latest https://example.com/photo.jpg
```

## 注意事项

- 首次运行会自动下载对应平台的二进制文件
- 临时文件会在执行结束后自动清理
- 需要网络连接以下载二进制和素材

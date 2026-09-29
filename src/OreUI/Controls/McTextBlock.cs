using System;
using System.Text;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Data;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Platform;

namespace OreUI.Controls;

/// <summary>
/// Minecraft 风格文本块：普通文字走 Minecraft 像素字体，
/// 基岩版 PUA 特殊字符（U+E000..U+E10C）直接渲染为本地内嵌的
/// <c>avares://OreUI/Assets/Emoji/eXXXX.png</c> 图标——资源来自开源可商用的
/// 重绘字形集（见 tools/fetch_open_icons.py 的替换流程），编译期随程序集嵌入，
/// 运行时零网络/云获取；某码点无对应图标时该字符处留空、不报错。
/// </summary>
public class McTextBlock : UserControl
{
    public static readonly StyledProperty<string?> TextProperty =
        AvaloniaProperty.Register<McTextBlock, string?>(nameof(Text));

    /// <summary>字形图标边长（设备无关像素）。留 NaN 则跟随 FontSize。</summary>
    public static readonly StyledProperty<double> GlyphSizeProperty =
        AvaloniaProperty.Register<McTextBlock, double>(nameof(GlyphSize), double.NaN);

    public string? Text
    {
        get => GetValue(TextProperty);
        set => SetValue(TextProperty, value);
    }

    public double GlyphSize
    {
        get => GetValue(GlyphSizeProperty);
        set => SetValue(GlyphSizeProperty, value);
    }

    private readonly WrapPanel _panel = new() { Orientation = Orientation.Horizontal };

    private static readonly Uri EmojiBase = new("avares://OreUI/Assets/Emoji/");

    public McTextBlock()
    {
        Content = _panel;
        PropertyChanged += (_, e) =>
        {
            if (e.Property == TextProperty || e.Property == GlyphSizeProperty || e.Property == FontSizeProperty)
                Render();
        };
    }

    private void Render()
    {
        _panel.Children.Clear();

        var text = Text ?? string.Empty;
        double size = double.IsNaN(GlyphSize) || GlyphSize <= 0
            ? (double.IsNaN(this.FontSize) ? 16 : this.FontSize)
            : GlyphSize;

        var sb = new StringBuilder();
        for (int i = 0; i < text.Length; i++)
        {
            int cp = char.ConvertToUtf32(text, i);
            if (char.IsSurrogate(text, i)) i++; // 跳过低代理项

            // 基岩版 PUA 字形区（社区库覆盖 U+E000..U+E10C）
            if (cp is >= 0xE000 and <= 0xE10C)
            {
                FlushText(sb, size);
                // 文件名即码点 4 位十六进制（如 0xE0C0 -> e0c0.png），资源随程序集本地嵌入
                var uri = new Uri(EmojiBase, $"{cp:X4}.png".ToLowerInvariant());
                _panel.Children.Add(new Image
                {
                    Width = size,
                    Height = size,
                    Stretch = Stretch.Uniform,
                    Source = TryLoad(uri),
                    VerticalAlignment = VerticalAlignment.Center,
                    Margin = new Thickness(1, 0, 1, 0),
                });
            }
            else
            {
                sb.Append(char.ConvertFromUtf32(cp));
            }
        }

        FlushText(sb, size);
    }

    private void FlushText(StringBuilder sb, double size)
    {
        if (sb.Length == 0) return;
        var tb = new TextBlock
        {
            Text = sb.ToString(),
            VerticalAlignment = VerticalAlignment.Center,
            FontFamily = this.FontFamily,
            FontSize = this.FontSize,
            FontWeight = this.FontWeight,
            FontStyle = this.FontStyle,
            LineHeight = size * 1.2,
        };
        // 绑定前景色：父级（如选中态 TabItem）改前景时能实时跟随（白字高亮）
        tb.Bind(TextBlock.ForegroundProperty,
                new Binding { Source = this, Path = nameof(Foreground) });
        _panel.Children.Add(tb);
        sb.Clear();
    }

    /// <summary>从内嵌资源加载字形图标；缺失时返回 null（字形处留空，不报错）。</summary>
    private static Bitmap? TryLoad(Uri uri)
    {
        try
        {
            using var stream = AssetLoader.Open(uri);
            return new Bitmap(stream);
        }
        catch
        {
            return null;
        }
    }
}

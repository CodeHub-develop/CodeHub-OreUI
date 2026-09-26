using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Layout;

namespace OreUI.Controls;

/// <summary>
/// 深色圆角面板容器，对应 OreUI 的 Panel。
/// </summary>
public class OrePanel : ContentControl
{
}

/// <summary>
/// 分隔线，对应 OreUI 的 Divider（横/竖，default/light/dark 三种变体）。
/// </summary>
public enum OreDividerVariant
{
    Default,
    Light,
    Dark
}

public class OreDivider : TemplatedControl
{
    public static readonly StyledProperty<Orientation> OrientationProperty =
        AvaloniaProperty.Register<OreDivider, Orientation>(nameof(Orientation), Orientation.Horizontal);

    public static readonly StyledProperty<OreDividerVariant> VariantProperty =
        AvaloniaProperty.Register<OreDivider, OreDividerVariant>(nameof(Variant), OreDividerVariant.Default);

    static OreDivider()
    {
        OrientationProperty.Changed.AddClassHandler<OreDivider>((x, _) => x.SyncClasses());
        VariantProperty.Changed.AddClassHandler<OreDivider>((x, _) => x.SyncClasses());
    }

    public Orientation Orientation
    {
        get => GetValue(OrientationProperty);
        set => SetValue(OrientationProperty, value);
    }

    public OreDividerVariant Variant
    {
        get => GetValue(VariantProperty);
        set => SetValue(VariantProperty, value);
    }

    private void SyncClasses()
    {
        Classes.Set("horizontal", Orientation == Orientation.Horizontal);
        Classes.Set("vertical", Orientation == Orientation.Vertical);
        Classes.Set("light", Variant == OreDividerVariant.Light);
        Classes.Set("dark", Variant == OreDividerVariant.Dark);
    }
}

/// <summary>
/// 加载指示（旋转环），对应 OreUI 的 Spinner。
/// </summary>
public class OreSpinner : ProgressBar
{
    public OreSpinner()
    {
        IsIndeterminate = true;
    }
}

/// <summary>
/// 标签/徽标，对应 OreUI 的 Tag（多种颜色变体）。
/// </summary>
public enum OreTagVariant
{
    Default,
    Success,
    Danger,
    Warning,
    Info
}

public class OreTag : ContentControl
{
    public static readonly StyledProperty<OreTagVariant> TagVariantProperty =
        AvaloniaProperty.Register<OreTag, OreTagVariant>(nameof(TagVariant), OreTagVariant.Default);

    static OreTag()
    {
        TagVariantProperty.Changed.AddClassHandler<OreTag>((x, _) => x.SyncClasses());
    }

    public OreTagVariant TagVariant
    {
        get => GetValue(TagVariantProperty);
        set => SetValue(TagVariantProperty, value);
    }

    private void SyncClasses()
    {
        Classes.Set("success", TagVariant == OreTagVariant.Success);
        Classes.Set("danger", TagVariant == OreTagVariant.Danger);
        Classes.Set("warning", TagVariant == OreTagVariant.Warning);
        Classes.Set("info", TagVariant == OreTagVariant.Info);
    }
}

/// <summary>
/// 顶部导航栏，对应 OreUI 的 Header（返回 / 面包屑标题 / 关闭）。
/// </summary>
public class OreHeader : ContentControl
{
    public static readonly StyledProperty<string?> TitleProperty =
        AvaloniaProperty.Register<OreHeader, string?>(nameof(Title));

    public static readonly StyledProperty<bool> ShowBackProperty =
        AvaloniaProperty.Register<OreHeader, bool>(nameof(ShowBack), true);

    public static readonly StyledProperty<bool> ShowCloseProperty =
        AvaloniaProperty.Register<OreHeader, bool>(nameof(ShowClose), false);

    public string? Title
    {
        get => GetValue(TitleProperty);
        set => SetValue(TitleProperty, value);
    }

    public bool ShowBack
    {
        get => GetValue(ShowBackProperty);
        set => SetValue(ShowBackProperty, value);
    }

    public bool ShowClose
    {
        get => GetValue(ShowCloseProperty);
        set => SetValue(ShowCloseProperty, value);
    }
}

/// <summary>
/// 菜单行，对应 OreUI 的 MenuRow（缩略图 + 标题 + 副标题 + › 箭头）。
/// </summary>
public class OreMenuRow : ContentControl
{
    static OreMenuRow()
    {
        IsSelectedProperty.Changed.AddClassHandler<OreMenuRow>((x, _) =>
            x.Classes.Set("selected", x.IsSelected));
    }

    public static readonly StyledProperty<object?> IconProperty =
        AvaloniaProperty.Register<OreMenuRow, object?>(nameof(Icon));

    public static readonly StyledProperty<string?> SubtitleProperty =
        AvaloniaProperty.Register<OreMenuRow, string?>(nameof(Subtitle));

    public static readonly StyledProperty<bool> ShowChevronProperty =
        AvaloniaProperty.Register<OreMenuRow, bool>(nameof(ShowChevron), true);

    public static readonly StyledProperty<bool> IsSelectedProperty =
        AvaloniaProperty.Register<OreMenuRow, bool>(nameof(IsSelected));

    public object? Icon
    {
        get => GetValue(IconProperty);
        set => SetValue(IconProperty, value);
    }

    public string? Subtitle
    {
        get => GetValue(SubtitleProperty);
        set => SetValue(SubtitleProperty, value);
    }

    public bool ShowChevron
    {
        get => GetValue(ShowChevronProperty);
        set => SetValue(ShowChevronProperty, value);
    }

    public bool IsSelected
    {
        get => GetValue(IsSelectedProperty);
        set => SetValue(IsSelectedProperty, value);
    }
}

/// <summary>
/// 选择列表，对应 OreUI 的 SelectionList（项用 OreMenuRow 风格渲染）。
/// </summary>
public class OreSelectionList : ListBox
{
}

/// <summary>
/// 模态层，对应 OreUI 的 Modal（半透明遮罩 + 居中面板）。
/// </summary>
public class OreModal : ContentControl
{
    public static readonly StyledProperty<bool> IsOpenProperty =
        AvaloniaProperty.Register<OreModal, bool>(nameof(IsOpen));

    public bool IsOpen
    {
        get => GetValue(IsOpenProperty);
        set => SetValue(IsOpenProperty, value);
    }
}

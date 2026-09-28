using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Platform;
using Avalonia.Threading;

namespace OreUI.Sample;

internal class Program
{
    [STAThread]
    private static void Main(string[] args)
    {
        // 离屏截图模式：--screenshot <png路径>
        // 使用 Avalonia Headless 纯软件渲染，不依赖窗口服务器，用于渲染验证。
        var shotIdx = Array.IndexOf(args, "--screenshot");
        if (shotIdx >= 0 && shotIdx + 1 < args.Length)
        {
            var path = args[shotIdx + 1];
            var app = BuildHeadlessApp().SetupWithoutStarting();
            var window = new MainWindow();
            window.Show();
            // headless 下没有消息循环，手动 pump Dispatcher 完成布局/渲染
            for (var i = 0; i < 40; i++)
            {
                Dispatcher.UIThread.RunJobs(DispatcherPriority.Background);
                Thread.Sleep(50);
            }
            var full = Path.GetFullPath(path);
            using (var frame = window.CaptureRenderedFrame())
            {
                if (frame is null)
                {
                    throw new InvalidOperationException("no rendered frame captured");
                }
                frame.Save(full);
            }
            Console.WriteLine($"saved {full} exists={File.Exists(full)} size={(File.Exists(full) ? new FileInfo(full).Length : 0)}");
            if (!File.Exists(full) || new FileInfo(full).Length == 0)
            {
                throw new IOException("screenshot file was not persisted");
            }
            return;
        }

        BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);
    }

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .LogToTrace();

    public static AppBuilder BuildHeadlessApp()
        => AppBuilder.Configure<App>()
            .UseHeadless(new AvaloniaHeadlessPlatformOptions())
            .LogToTrace();
}

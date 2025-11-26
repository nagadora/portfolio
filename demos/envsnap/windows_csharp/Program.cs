// envsnap/windows_csharp/Program.cs
using System.Diagnostics;
using System.Text;
using System.Windows.Forms;

static class Program
{
    [STAThread]
    static int Main(string[] args)
    {
        try
        {
            // コンソール出力をUTF-8に（表示側が対応してないと文字化けすることはある）
            Console.OutputEncoding = Encoding.UTF8;

            var root = FindProjectRoot(AppContext.BaseDirectory);
            var pythonCoreDir = Path.Combine(root, "python_core");
            var collectPy = Path.Combine(pythonCoreDir, "collect.py");

            var python = ChoosePythonExecutable();
            if (python is null)
            {
                Console.Error.WriteLine(
                    "Python が見つかりません。PATH か、環境変数 ENVSNAP_PYTHON で python.exe の場所を指定してください。");
                return 2;
            }

            // PythonにUTF-8で出力させる（これが文字化け対策の本命）
            var arguments = BuildPythonArgs(python, collectPy);

            var reportText = RunProcess(
                fileName: python,
                arguments: arguments,
                workingDir: pythonCoreDir
            );

            if (string.IsNullOrWhiteSpace(reportText))
            {
                Console.Error.WriteLine("EnvSnap の出力が空でした。");
                return 3;
            }

            // クリップボードは基本UTF-16なので、ここは通常化けない
            Clipboard.SetText(reportText);

            Console.WriteLine(reportText);
            Console.WriteLine();
            Console.WriteLine("Copied to clipboard.");
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.ToString());
            return 1;
        }
    }

    static string? ChoosePythonExecutable()
    {
        // 1) 明示指定（最優先）：ENVSNAP_PYTHON=C:\...\python.exe
        var env = Environment.GetEnvironmentVariable("ENVSNAP_PYTHON");
        if (!string.IsNullOrWhiteSpace(env) && File.Exists(env) && CanRun(env, "--version"))
            return env;

        // 2) Python Launcher（Windowsの定番）
        if (CanRun("py", "-V")) return "py";

        // 3) いつもの python / python3
        if (CanRun("python", "--version")) return "python";
        if (CanRun("python3", "--version")) return "python3";

        return null;
    }

    static string BuildPythonArgs(string pythonCmdOrPath, string collectPyPath)
    {
        // UTF-8強制：-X utf8 + PYTHONUTF8/PYTHONIOENCODING をRunProcess側で付与
        // pyの場合は「py -3 -X utf8 script.py ...」の形にする
        var script = Quote(collectPyPath);

        if (pythonCmdOrPath == "py")
        {
            return $"-3 -X utf8 {script} --format text";
        }

        return $"-X utf8 {script} --format text";
    }

    static bool CanRun(string fileName, string arguments)
    {
        try
        {
            using var p = new Process();
            p.StartInfo = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = arguments,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8,
            };

            // UTF-8で吐かせる（--versionでも一応）
            p.StartInfo.EnvironmentVariables["PYTHONUTF8"] = "1";
            p.StartInfo.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";

            p.Start();
            p.WaitForExit(1500);
            return p.ExitCode == 0 || p.ExitCode == 2; // python --version が stderr に出る環境もある
        }
        catch
        {
            return false;
        }
    }

    static string RunProcess(string fileName, string arguments, string workingDir)
    {
        using var p = new Process();
        p.StartInfo = new ProcessStartInfo
        {
            FileName = fileName,
            Arguments = arguments,
            WorkingDirectory = workingDir,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8,
            CreateNoWindow = true
        };

        // これが効く：Python側の出力をUTF-8固定
        p.StartInfo.EnvironmentVariables["PYTHONUTF8"] = "1";
        p.StartInfo.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";

        p.Start();
        var stdout = p.StandardOutput.ReadToEnd();
        var stderr = p.StandardError.ReadToEnd();
        p.WaitForExit();

        if (p.ExitCode != 0)
        {
            throw new InvalidOperationException(
                $"Python failed.\nExitCode={p.ExitCode}\nSTDERR:\n{stderr}\nSTDOUT:\n{stdout}"
            );
        }

        return stdout;
    }

    static string FindProjectRoot(string startDir)
    {
        var dir = new DirectoryInfo(startDir);
        for (int i = 0; i < 10 && dir is not null; i++)
        {
            var candidate = Path.Combine(dir.FullName, "python_core", "collect.py");
            if (File.Exists(candidate)) return dir.FullName;
            dir = dir.Parent;
        }
        throw new DirectoryNotFoundException("envsnap のルートが見つかりません（python_core/collect.py が必要）。");
    }

    static string Quote(string path)
        => path.Contains(' ') ? $"\"{path}\"" : path;
}
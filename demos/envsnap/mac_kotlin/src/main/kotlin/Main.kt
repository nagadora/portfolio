import java.io.File

fun main() {
    val root = findProjectRoot(File(".").absoluteFile)
    val pythonCore = File(root, "python_core")
    val collectPy = File(pythonCore, "collect.py").absolutePath

    val python = choosePython() ?: run {
        System.err.println("python3 / python が見つかりません。PATH に入れてください。")
        return
    }

    // Python側のUTF-8強制（可能なら -X utf8 を付ける）
    val args = if (python == "python3" || python == "python") {
        listOf("-X", "utf8", collectPy, "--format", "text")
    } else {
        listOf(collectPy, "--format", "text")
    }

    val text = runProcess(python, args, workDir = pythonCore)
    if (text.isBlank()) {
        System.err.println("EnvSnap の出力が空でした。")
        return
    }

    // クリップボードへ
    runProcess("pbcopy", emptyList(), input = text)

    println(text)
    println()
    println("Copied to clipboard.")
}

private fun choosePython(): String? {
    if (canRun("python3", listOf("--version"))) return "python3"
    if (canRun("python", listOf("--version"))) return "python"
    return null
}

private fun canRun(cmd: String, args: List<String>): Boolean {
    return try {
        val pb = ProcessBuilder(listOf(cmd) + args)
        pb.redirectErrorStream(true)

        // ★ここも入れておくと事故りにくい（Pythonの場合）
        pb.environment()["PYTHONUTF8"] = "1"
        pb.environment()["PYTHONIOENCODING"] = "utf-8"

        val p = pb.start()
        p.inputStream.bufferedReader(Charsets.UTF_8).readText()
        p.waitFor()
        p.exitValue() == 0
    } catch (_: Exception) {
        false
    }
}

private fun runProcess(
    cmd: String,
    args: List<String>,
    workDir: File? = null,
    input: String? = null
): String {
    val pb = ProcessBuilder(listOf(cmd) + args)
    if (workDir != null) pb.directory(workDir)
    pb.redirectErrorStream(true)

    // ★ここが本命：Pythonの標準出力をUTF-8固定
    pb.environment()["PYTHONUTF8"] = "1"
    pb.environment()["PYTHONIOENCODING"] = "utf-8"

    val p = pb.start()

    if (input != null) {
        p.outputStream.bufferedWriter(Charsets.UTF_8).use { it.write(input) }
    }

    val out = p.inputStream.bufferedReader(Charsets.UTF_8).readText()
    p.waitFor()

    if (p.exitValue() != 0) {
        throw RuntimeException("Process failed: $cmd ${args.joinToString(" ")}\n$out")
    }
    return out
}

private fun findProjectRoot(start: File): File {
    var cur: File? = start
    repeat(10) {
        val candidate = File(cur, "python_core/collect.py")
        if (candidate.exists()) return cur!!
        cur = cur?.parentFile
    }
    error("envsnap のルートが見つかりません（python_core/collect.py が必要）。")
}
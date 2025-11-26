import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import kotlinx.serialization.Serializable
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

@Serializable
data class LogEntry(
    val id: Int,
    val date: String,
    val content: String,
    val tags: List<String> = emptyList()
)

object LogRepository {
    private val file: Path = Paths.get("creator_flow_log_gui.json")
    private val json = Json {
        prettyPrint = true
        ignoreUnknownKeys = true
    }

    // List<LogEntry> 専用のシリアライザを事前に用意しておく
	private val logEntryListSerializer = ListSerializer(LogEntry.serializer())

    fun load(): List<LogEntry> {
        if (!Files.exists(file)) return emptyList()
        val text = Files.readString(file)
        if (text.isBlank()) return emptyList()

        return try {
            // ★ 型を明示して decode（反射を使わない）
            json.decodeFromString(logEntryListSerializer, text)
        } catch (e: Exception) {
            println("読み込みに失敗: ${e.message}")
            emptyList()
        }
    }

    fun save(entries: List<LogEntry>) {
        // ★ こちらも同じ serializer を明示
        val text = json.encodeToString(logEntryListSerializer, entries)
        Files.writeString(file, text)
    }
}



private val DarkColors = darkColors(
    primary = Color(0xFF4F46E5),
    background = Color(0xFF0F172A),
    surface = Color(0xFF111827),
    onPrimary = Color.White,
    onBackground = Color(0xFFE5E7EB),
    onSurface = Color(0xFFE5E7EB),
)


@Composable
fun CreatorFlowLogApp() {
    MaterialTheme(colors = DarkColors) {
        Surface(modifier = Modifier.fillMaxSize()) {
            CreatorFlowLogScreen()
        }
    }
}


@Composable
fun CreatorFlowLogScreen() {
    var logs by remember { mutableStateOf(LogRepository.load()) }

    var searchText by remember { mutableStateOf("") }

    var dateInput by remember {
        mutableStateOf(LocalDate.now().format(DateTimeFormatter.ISO_DATE))
    }
    var contentInput by remember { mutableStateOf("") }
    var tagsInput by remember { mutableStateOf("") }

    var selectedLog by remember { mutableStateOf<LogEntry?>(null) }

    val filteredLogs = logs.filter { entry ->
        if (searchText.isBlank()) true else {
            val q = searchText.lowercase()
            entry.content.lowercase().contains(q) ||
                    entry.date.lowercase().contains(q) ||
                    entry.tags.any { it.lowercase().contains(q) }
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {

        TopAppBar(
            backgroundColor = Color(0xFF020617),
            contentColor = Color.White
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth().padding(16.dp)
            ) {
                Text("Creator Flow Log", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.weight(1f))

                OutlinedTextField(
                    value = searchText,
                    onValueChange = { searchText = it },
                    placeholder = { Text("検索") },
                    singleLine = true,
                    modifier = Modifier.width(240.dp)
                )
            }
        }

        Row(modifier = Modifier.fillMaxSize().padding(16.dp)) {
            Column(modifier = Modifier.weight(3f)) {
                Text("ログ一覧", fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                LogTable(filteredLogs) { selectedLog = it }
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(2f)) {
                SelectedLogPanel(selectedLog)

                Spacer(modifier = Modifier.height(24.dp))

                Text("新規追加", fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = dateInput,
                    onValueChange = { dateInput = it },
                    label = { Text("日付") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = contentInput,
                    onValueChange = { contentInput = it },
                    label = { Text("内容") },
                    modifier = Modifier.fillMaxWidth().height(80.dp)
                )

                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = tagsInput,
                    onValueChange = { tagsInput = it },
                    label = { Text("タグ（カンマ区切り）") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = {
                        val nextId = (logs.maxOfOrNull { it.id } ?: 0) + 1
                        val tags = tagsInput.split(",").map { it.trim() }.filter { it.isNotEmpty() }

                        val newLog = LogEntry(
                            id = nextId,
                            date = dateInput,
                            content = contentInput,
                            tags = tags
                        )

                        logs = logs + newLog
                        LogRepository.save(logs)

                        dateInput = LocalDate.now().format(DateTimeFormatter.ISO_DATE)
                        contentInput = ""
                        tagsInput = ""
                    },
                    modifier = Modifier.align(Alignment.End)
                ) {
                    Text("追加")
                }
            }
        }
    }
}
@Composable
fun LogTable(logs: List<LogEntry>, onClick: (LogEntry) -> Unit) {
    val scroll = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF020617))
            .verticalScroll(scroll)
    ) {
        logs.forEach { entry ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onClick(entry) }
                    .padding(8.dp)
            ) {
                Text("${entry.id}", modifier = Modifier.width(40.dp))
                Text(entry.date, modifier = Modifier.width(100.dp))
                Text(
                    entry.content,
                    modifier = Modifier.weight(1f),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
        }
    }
}
@Composable
fun SelectedLogPanel(selectedLog: LogEntry?) {
    Card(
        backgroundColor = Color(0xFF020617),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text("選択中の記録", fontWeight = FontWeight.Bold)

            if (selectedLog == null) {
                Text("左の一覧から選択すると詳細が表示されます。", color = Color(0xFF9CA3AF))
            } else {
                Text("#${selectedLog.id}  ${selectedLog.date}", fontWeight = FontWeight.Bold)
                Text(selectedLog.content)
                Text("タグ: ${selectedLog.tags.joinToString()}")
            }
        }
    }
}
fun main() = application {
    Window(onCloseRequest = { exitApplication() }, title = "Creator Flow Log") {
        CreatorFlowLogApp()
    }
}
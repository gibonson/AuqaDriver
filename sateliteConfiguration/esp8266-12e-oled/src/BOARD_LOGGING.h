
const int LOG_SIZE = 10;
String logs[LOG_SIZE];
int logIndex = 0;
int logCount = 0;


// Dodaje nowy wpis do logów (ring buffer)
void addLog(const String entry)
{
  logs[logIndex] = entry;
  logIndex = (logIndex + 1) % LOG_SIZE;
  if (logCount < LOG_SIZE)
    logCount++;
}

String getLogs()
{
  String result = "";
  int start = (logIndex + LOG_SIZE - logCount) % LOG_SIZE;
  for (int i = 0; i < logCount; i++)
  {
    int idx = (start + i) % LOG_SIZE;
    if (logs[idx].length() > 0)
    { // Pomija puste wpisy
      result += logs[idx] + "\n";
    }
  }
  return result;
}
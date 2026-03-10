package com.example.mad.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.net.URI

class MediaRepository(
    private val client: OkHttpClient = HttpClientProvider.client
) {
    private val imageExtensions = setOf("jpg", "jpeg", "png", "webp", "gif")
    private val videoExtensions = setOf("mp4", "webm", "mkv", "mov")
    private val linkRegex = Regex("<a\\s+[^>]*href=[\"']([^\"']+)[\"']", RegexOption.IGNORE_CASE)
    private val maxDepth = 3

    suspend fun fetchMedia(baseUrl: String): List<MediaItem> = withContext(Dispatchers.IO) {
        val normalizedBaseUrl = if (baseUrl.endsWith("/")) baseUrl else "$baseUrl/"
        val results = mutableListOf<MediaItem>()
        val visited = mutableSetOf<String>()

        // Nginx autoindex is HTML, so we crawl the <a href="..."> links.
        fetchDirectory(normalizedBaseUrl, 0, visited, results)
        results
    }

    private suspend fun fetchDirectory(
        url: String,
        depth: Int,
        visited: MutableSet<String>,
        results: MutableList<MediaItem>
    ) {
        if (depth > maxDepth || !visited.add(url)) {
            // Depth limit + visited check stops endless loops in folder links.
            return
        }

        val request = Request.Builder().url(url).build()
        val response = client.newCall(request).execute()
        if (!response.isSuccessful) {
            response.close()
            return
        }

        val body = response.body?.string().orEmpty()
        response.close()

        val baseUri = URI(url)

        linkRegex.findAll(body).forEach { match ->
            val href = match.groupValues[1]
            if (href.isBlank() || href == "../" || href.startsWith("?") || href.startsWith("#")) {
                return@forEach
            }

            val resolvedUrl = baseUri.resolve(href).toString()

            if (href.endsWith("/")) {
                fetchDirectory(resolvedUrl, depth + 1, visited, results)
                return@forEach
            }

            val extension = href.substringAfterLast('.', "").lowercase()
            val type = when {
                extension in imageExtensions -> MediaType.Image
                extension in videoExtensions -> MediaType.Video
                else -> null
            }

            if (type != null) {
                results.add(
                    MediaItem(
                        id = resolvedUrl,
                        type = type,
                        url = resolvedUrl
                    )
                )
            }
        }
    }
}

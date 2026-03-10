package com.example.mad.data

import okhttp3.Interceptor
import okhttp3.OkHttpClient

object HttpClientProvider {
    val client: OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(Interceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("X-App-Key", "Yoda I Am!")
                .build()
            chain.proceed(request)
        })
        .hostnameVerifier { _, _ -> true } // FIXME: Not for production
        .build()
}

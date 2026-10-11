/* Mirrors QZD 17.3 DecompressorLZMA (src/common/filesystem/source/files_decompress.cpp)
   byte for byte in its control flow, using the repo's own LzmaDec.c.
   Input: a file of records: u32 compsize, u32 uncompsize, u32 chunk, comp bytes.
   Output: decoded bytes to stdout-file for each record. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "LzmaDec.h"
static void *SzAlloc(ISzAllocPtr p, size_t size) { (void)p; return malloc(size); }
static void SzFree(ISzAllocPtr p, void *a) { (void)p; free(a); }
static ISzAlloc g_Alloc = { SzAlloc, SzFree };
enum { BUFF_SIZE = 4096 };
typedef struct { const unsigned char *data; size_t size, pos; } Reader;
static size_t rd(Reader *r, void *buf, size_t n) { size_t k = r->size - r->pos; if (k > n) k = n; memcpy(buf, r->data + r->pos, k); r->pos += k; return k; }
typedef struct { Reader *File; int SawEOF; CLzmaDec Stream; size_t InPos, InSize; unsigned char InBuff[BUFF_SIZE]; } Dec;
static void FillBuffer(Dec *d) { size_t n = rd(d->File, d->InBuff, BUFF_SIZE); if (n < BUFF_SIZE) d->SawEOF = 1; d->InPos = 0; d->InSize = n; }
static int Open(Dec *d, Reader *f) {
  unsigned char header[4 + LZMA_PROPS_SIZE]; d->File = f; d->SawEOF = 0;
  if (rd(f, header, sizeof header) < sizeof header) { fprintf(stderr, "too short\n"); return 0; }
  if (header[2] + header[3] * 256 != LZMA_PROPS_SIZE) { fprintf(stderr, "props size %d\n", header[2] + header[3] * 256); return 0; }
  FillBuffer(d); LzmaDec_Construct(&d->Stream);
  if (LzmaDec_Allocate(&d->Stream, header + 4, LZMA_PROPS_SIZE, &g_Alloc) != SZ_OK) { fprintf(stderr, "alloc\n"); return 0; }
  LzmaDec_Init(&d->Stream); return 1;
}
static long Read(Dec *d, void *buffer, long len) {
  int err; Byte *next_out = (Byte *)buffer;
  do {
    ELzmaFinishMode finish_mode = LZMA_FINISH_ANY; ELzmaStatus status;
    size_t out_processed = len; size_t in_processed = d->InSize;
    err = LzmaDec_DecodeToBuf(&d->Stream, next_out, &out_processed, d->InBuff + d->InPos, &in_processed, finish_mode, &status);
    d->InPos += in_processed; d->InSize -= in_processed; next_out += out_processed; len = (long)(len - out_processed);
    if (err != SZ_OK) { fprintf(stderr, "Corrupt LZMA stream\n"); return -1; }
    if (in_processed == 0 && out_processed == 0) { if (status != LZMA_STATUS_FINISHED_WITH_MARK) { fprintf(stderr, "Corrupt LZMA stream (stall)\n"); return -1; } }
    if (d->InSize == 0 && !d->SawEOF) FillBuffer(d);
  } while (err == SZ_OK && len != 0);
  if (len != 0) { fprintf(stderr, "Ran out of data in LZMA stream\n"); return -1; }
  return (long)(next_out - (Byte *)buffer);
}
int main(int argc, char **argv) {
  FILE *in = fopen(argv[1], "rb"), *out = fopen(argv[2], "wb"); unsigned hdr[3]; int n = 0;
  while (fread(hdr, 4, 3, in) == 3) {
    unsigned char *c = malloc(hdr[0]); fread(c, 1, hdr[0], in);
    Reader r = { c, hdr[0], 0 }; Dec *d = calloc(1, sizeof *d);
    if (!Open(d, &r)) return 2;
    unsigned char *o = malloc(hdr[1] + 1); long got = 0;
    while (got < (long)hdr[1]) { long want = hdr[2] ? (long)hdr[2] : (long)hdr[1]; if (want > (long)hdr[1] - got) want = hdr[1] - got;
      long k = Read(d, o + got, want); if (k < 0) return 3; got += k; }
    fwrite(o, 1, hdr[1], out); LzmaDec_Free(&d->Stream, &g_Alloc); free(d); free(o); free(c); n++;
  }
  fprintf(stderr, "decoded %d entries\n", n); fclose(out); return 0;
}

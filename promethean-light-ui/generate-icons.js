import sharp from 'sharp';
import fs from 'fs';
import path from 'path';

const iconsDir = './src-tauri/icons';

// Create a simple orange fire/flame icon as PNG
const size = 256;
const svg = `
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="fireGrad" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" style="stop-color:#f97316"/>
      <stop offset="50%" style="stop-color:#fb923c"/>
      <stop offset="100%" style="stop-color:#fbbf24"/>
    </linearGradient>
  </defs>
  <rect width="${size}" height="${size}" rx="48" fill="#1a1a2e"/>
  <g transform="translate(${size/2}, ${size/2 + 20})">
    <path d="M0,-90
             C30,-70 40,-40 35,-10
             C50,-30 60,-20 55,20
             C70,0 75,30 60,60
             C45,80 20,85 0,85
             C-20,85 -45,80 -60,60
             C-75,30 -70,0 -55,20
             C-60,-20 -50,-30 -35,-10
             C-40,-40 -30,-70 0,-90 Z"
          fill="url(#fireGrad)"/>
    <ellipse cx="0" cy="40" rx="25" ry="35" fill="#fef3c7" opacity="0.8"/>
  </g>
</svg>
`;

// Create ICO file manually (proper format)
function createIco(pngBuffers) {
  // ICO header: 6 bytes
  // Image entries: 16 bytes each
  // Then PNG data for each

  const numImages = pngBuffers.length;
  const headerSize = 6;
  const entrySize = 16;
  const dataOffset = headerSize + (numImages * entrySize);

  let totalSize = dataOffset;
  for (const buf of pngBuffers) {
    totalSize += buf.length;
  }

  const ico = Buffer.alloc(totalSize);

  // ICO Header
  ico.writeUInt16LE(0, 0);      // Reserved
  ico.writeUInt16LE(1, 2);      // Type: 1 = ICO
  ico.writeUInt16LE(numImages, 4); // Number of images

  let currentOffset = dataOffset;
  const sizes = [256, 48, 32, 16];

  for (let i = 0; i < numImages; i++) {
    const buf = pngBuffers[i];
    const size = sizes[i];
    const entryOffset = headerSize + (i * entrySize);

    ico.writeUInt8(size === 256 ? 0 : size, entryOffset);     // Width (0 = 256)
    ico.writeUInt8(size === 256 ? 0 : size, entryOffset + 1); // Height (0 = 256)
    ico.writeUInt8(0, entryOffset + 2);                        // Color palette
    ico.writeUInt8(0, entryOffset + 3);                        // Reserved
    ico.writeUInt16LE(1, entryOffset + 4);                     // Color planes
    ico.writeUInt16LE(32, entryOffset + 6);                    // Bits per pixel
    ico.writeUInt32LE(buf.length, entryOffset + 8);            // Size of image data
    ico.writeUInt32LE(currentOffset, entryOffset + 12);        // Offset to image data

    buf.copy(ico, currentOffset);
    currentOffset += buf.length;
  }

  return ico;
}

async function generateIcons() {
  // Ensure icons directory exists
  if (!fs.existsSync(iconsDir)) {
    fs.mkdirSync(iconsDir, { recursive: true });
  }

  const buffer = Buffer.from(svg);

  // Generate PNG files
  const pngSizes = [
    { name: '32x32.png', size: 32 },
    { name: '128x128.png', size: 128 },
    { name: '128x128@2x.png', size: 256 },
    { name: 'icon.png', size: 256 },
  ];

  for (const { name, size } of pngSizes) {
    await sharp(buffer)
      .resize(size, size)
      .png()
      .toFile(path.join(iconsDir, name));
    console.log(`Created ${name}`);
  }

  // Generate ICO with multiple sizes
  const icoSizes = [256, 48, 32, 16];
  const pngBuffers = [];

  for (const size of icoSizes) {
    const pngBuf = await sharp(buffer)
      .resize(size, size)
      .png()
      .toBuffer();
    pngBuffers.push(pngBuf);
  }

  const icoBuffer = createIco(pngBuffers);
  fs.writeFileSync(path.join(iconsDir, 'icon.ico'), icoBuffer);
  console.log('Created icon.ico (proper format)');

  console.log('All icons generated!');
}

generateIcons().catch(console.error);

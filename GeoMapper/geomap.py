import math

class GeoMap(object):
    """GeoMap will draw a map given a location, zoom, and public tile server."""
    
    # List of public map tile Z/X/Y map tile servers.
    tile_servers = {
        # http://maps.stamen.com/
        'toner'              : "http://tile.stamen.com/toner/%s/%s/%s.png",
        'toner-lines'        : "http://tile.stamen.com/toner-lines/%s/%s/%s.png",
        'toner-hybrid'       : "http://tile.stamen.com/toner-hybrid/%s/%s/%s.png",
        'toner-background'   : "http://tile.stamen.com/toner-background/%s/%s/%s.png",
        'toner-lite'         : "http://tile.stamen.com/toner-lite/%s/%s/%s.png",
        'terrain'            : "http://tile.stamen.com/terrain/%s/%s/%s.png",
        'terrain-lines'      : "http://tile.stamen.com/terrain-lines/%s/%s/%s.png",
        'terrain-background' : "http://tile.stamen.com/terrain-background/%s/%s/%s.png",
        'watercolor'         : "http://tile.stamen.com/watercolor/%s/%s/%s.png",
        
        # Found in https://github.com/dfacts/staticmaplite/blob/master/staticmap.php
        'mapnik'             : "http://tile.openstreetmap.org/%s/%s/%s.png",
        'cycle'              : "http://a.tile.opencyclemap.org/cycle/%s/%s/%s.png",
        
        # http://wiki.openstreetmap.org/wiki/Tile_servers
        'openstreetmap'      : "http://a.tile.openstreetmap.org/%s/%s/%s.png", # also http://b.* and https://c.*
        'wikimedia'          : "https://maps.wikimedia.org/osm-intl/%s/%s/%s.png",
        'carto-light'         : "http://a.basemaps.cartocdn.com/light_all/%s/%s/%s.png",
        'carto-dark'          : "http://a.basemaps.cartocdn.com/dark_all/%s/%s/%s.png",
        'openptmap'          : "http://www.openptmap.org/tiles/%s/%s/%s.png",
        'hikebike'           : "http://a.tiles.wmflabs.org/hikebike/%s/%s/%s.png",
        
        # https://carto.com/location-data-services/basemaps/
        # Note: These seem to be really slow.
        'carto-lightall'     : "http://cartodb-basemaps-1.global.ssl.fastly.net/light_all/%s/%s/%s.png",
        'carto-darkall'      : "http://cartodb-basemaps-1.global.ssl.fastly.net/dark_all/%s/%s/%s.png",
        'carto-lightnolabels': "http://cartodb-basemaps-1.global.ssl.fastly.net/light_nolabels/%s/%s/%s.png",
        'carto-darknolabels' : "http://cartodb-basemaps-1.global.ssl.fastly.net/dark_nolabels/%s/%s/%s.png",
        }
    
    tileSize = 256.0
    
    def __init__(self, lat, lon, zoom, w, h, server='toner'):
        self.baseMap = createGraphics(w, h)
        
        if server in self.tile_servers:
            self.url = self.tile_servers[server]
        else:
            print "Got %s as a tile server but that didn't exist. Available servers are %s. Falling back to 'toner'." % \
                (server, ", ".join(self.tile_servers.keys()))
            self.url = self.tile_servers['toner']
        
        self.lat = lat
        self.lon = lon
        self.zoom = min(zoom, 18)
        self.w = w
        self.h = h
        
        self.centerX = lonToTile(self.lon, self.zoom)
        self.centerY = latToTile(self.lat, self.zoom)
        self.offsetX = floor((floor(self.centerX) - self.centerX) * self.tileSize)
        self.offsetY = floor((floor(self.centerY) - self.centerY) * self.tileSize)
    
    # Inspired by math contained in https://github.com/dfacts/staticmaplite/
    def createBaseMap(self):
        """Create the map by requesting tiles from the specified tile server."""
        
        startX = floor(self.centerX - (self.w / self.tileSize) / 2.0)
        startY = floor(self.centerY - (self.h / self.tileSize) / 2.0)
        
        endX = ceil(self.centerX + (self.w / self.tileSize) / 2.0)
        endY = ceil(self.centerY + (self.h / self.tileSize) / 2.0)
        
        self.offsetX = -floor((self.centerX - floor(self.centerX)) * self.tileSize) + \
            floor(self.w / 2.0) + \
            floor(startX - floor(self.centerX)) * self.tileSize
        self.offsetY = -floor((self.centerY - floor(self.centerY)) * self.tileSize) + \
            floor(self.h / 2.0) + \
            floor(startY - floor(self.centerY)) * self.tileSize
        
        self.baseMap.beginDraw()
        
        for x in xrange(startX, endX):
            for y in xrange(startY, endY):
                # 12/1208/1541.png
                url = self.url % (self.zoom, x, y)
                
                # Request the image and block until we get it.
                # TODO: Try requestImage() and some callback mechanism.
                tile = loadImage(url)
                
                destX = (x - startX) * self.tileSize + self.offsetX
                destY = (y - startY) * self.tileSize + self.offsetY
                
                if tile is not None:
                    self.baseMap.image(tile, destX, destY)
                else:
                    print "Error loading tile at %s" % url
        
        self.baseMap.endDraw()
        
    def makeGrayscale(self):
        self.baseMap.loadPixels()
        
        for i in xrange(0, self.baseMap.width * self.baseMap.height):
            b = self.baseMap.brightness(self.baseMap.pixels[i])
            self.baseMap.pixels[i] = self.baseMap.color(b, b, b)
        
        self.baseMap.updatePixels()
    
    def makeFaded(self):
        self.baseMap.noStroke()
        self.baseMap.fill(255, 255, 255, 128)
        self.baseMap.rect(0, 0, width, height)
    
    def draw(self):
        """Draws the base map on the Processing sketch canvas."""
        image(self.baseMap, 0, 0)
    
    def drawMarker(self, markerLat, markerLon, *meta):
        """Draws a circular marker in the main Processing PGraphics space."""
        
        x = self.lonToX(markerLon)
        y = self.latToY(markerLat)
        
        ellipse(x, y, 7, 7)
    
    def lonToX(self, lon):
        return floor((self.w / 2.0) - self.tileSize * (self.centerX - lonToTile(lon, self.zoom)))
    
    def latToY(self, lat):
        return floor((self.h / 2.0) - self.tileSize * (self.centerY - latToTile(lat, self.zoom)))
    
def lonToTile(lon, zoom):
    """Given a longitude and zoom value, return the X map tile index."""
    return ((lon + 180) / 360) * pow(2, zoom)

def latToTile(lat, zoom):
    """Given a latitude and zoom value, return the Y map tile index."""
    return (1 - log(tan(lat * math.pi / 180) + 1 / cos(lat * math.pi / 180)) / math.pi) / 2 * pow(2, zoom)